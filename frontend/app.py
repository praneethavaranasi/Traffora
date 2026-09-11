import warnings
warnings.filterwarnings("ignore")

import os
import json
import urllib.parse
import base64
from datetime import datetime, timedelta
import streamlit as st
import requests

# -------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION (COLLAPSED STREAMLIT CHROME)
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Traffora | Smart Traffic",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="auto"
)

# -------------------------------------------------------------------
# 2. QUERY PARAMETER ROUTING & SESSION STATE
# -------------------------------------------------------------------
query_page = st.query_params.get("page", "Dashboard")
if "page" not in st.session_state or st.session_state["page"] != query_page:
    st.session_state["page"] = query_page

page_clean = st.session_state["page"]

def nav_url(target_page):
    encoded = urllib.parse.quote(target_page)
    return f"?page={encoded}"

API_BASE_URL = "http://127.0.0.1:8000"

def api_get(path, params=None):
    try:
        r = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=2.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def api_post(path, payload):
    try:
        r = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=4.0)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None

# Fallback exact data from reference specification
FALLBACK_STATS = {
    "traffic_status": "Moderate",
    "traffic_status_desc": "Citywide Traffic Condition",
    "average_speed": "26.4 km/h",
    "speed_change": "↓ 8%",
    "congested_roads": 7,
    "congested_roads_change": "↑ 2",
    "active_incidents": 5,
    "total_records": 40000,
    "congestion": {
        "low_pct": 66.7,
        "mod_pct": 25.2,
        "high_pct": 8.1
    }
}

FALLBACK_TOP_ROADS = [
    {"rank": 1, "route": "HITEC City → Madhapur", "level": "High", "pct": 78},
    {"rank": 2, "route": "Kukatpally → Miyapur", "level": "High", "pct": 72},
    {"rank": 3, "route": "Ameerpet → Begumpet", "level": "Moderate", "pct": 61},
    {"rank": 4, "route": "LB Nagar → Uppal", "level": "Moderate", "pct": 53},
    {"rank": 5, "route": "Banjara Hills → Jubilee Hills", "level": "Moderate", "pct": 48},
]

def get_current_incidents():
    now = datetime.now()
    t1 = (now - timedelta(minutes=25)).strftime("%I:%M %p")
    t2 = (now - timedelta(minutes=65)).strftime("%I:%M %p")
    t3 = (now - timedelta(minutes=10)).strftime("%I:%M %p")
    return [
        {
            "id": 1,
            "badge": "Accident",
            "severity_color": "red",
            "time": t1,
            "text": "Minor accident reported on Outer Ring Road",
            "location": "Near Gachibowli Flyover",
            "icon": "alert-triangle"
        },
        {
            "id": 2,
            "badge": "Road Work",
            "severity_color": "orange",
            "time": t2,
            "text": "Road work in progress",
            "location": "Madhapur Main Road",
            "icon": "alert-triangle"
        },
        {
            "id": 3,
            "badge": "Heavy Traffic",
            "severity_color": "red",
            "time": t3,
            "text": "Heavy traffic due to signal issue",
            "location": "Ameerpet Junction",
            "icon": "alert-triangle"
        }
    ]

FALLBACK_INCIDENTS = get_current_incidents()

import re

def render_html(html_str):
    # Strip HTML comments to prevent markdown block confusion
    no_comments = re.sub(r'<!--.*?-->', '', html_str, flags=re.DOTALL)
    # Strip leading and trailing whitespace from every line so markdown NEVER interprets 4+ spaces as a code block (<pre><code>)
    clean_lines = [line.strip() for line in no_comments.splitlines() if line.strip()]
    st.markdown("\n".join(clean_lines), unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3. EMBED STYLES & GEIST SANS CSS
# -------------------------------------------------------------------
css_file_path = os.path.join(os.path.dirname(__file__), "styles", "main.css")
main_css_content = ""
if os.path.exists(css_file_path):
    with open(css_file_path, "r", encoding="utf-8") as f:
        main_css_content = f.read()

font_links = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-sans/style.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
"""

render_html(f"{font_links}<style>{main_css_content}</style>")

# -------------------------------------------------------------------
# 4. LUCIDE ICONS AS INLINE SVG HELPERS
# -------------------------------------------------------------------
ICONS = {
    "dashboard": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    "activity": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.48 12H2"/></svg>',
    "trending-up": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "navigation": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>',
    "alert-triangle": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "file-text": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "bar-chart-2": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>',
    "settings": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    "help-circle": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>',
    "layers": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    "car": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>',
    "gauge": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>',
    "traffic-jam": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 6h2a2 2 0 0 1 2 2v2"/><path d="M6 10h12"/><path d="M6 14h12"/><rect width="18" height="14" x="3" y="6" rx="2"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg>',
    "cloud": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
    "cloud-sun": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="M20 12h2"/><path d="m19.07 4.93-1.41 1.41"/><path d="M15.947 12.65a4 4 0 0 0-5.925-4.128"/><path d="M13 22H7a5 5 0 1 1 4.9-6H13a3 3 0 0 1 0 6Z"/></svg>',
    "cloudy": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 21H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/><path d="M22 10a3 3 0 0 0-3-3h-2.207a5.502 5.502 0 0 0-10.702.5"/></svg>',
    "cloud-rain": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/></svg>',
    "cloud-drizzle": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M8 19v1"/><path d="M8 14v1"/><path d="M16 19v1"/><path d="M16 14v1"/><path d="M12 21v1"/><path d="M12 16v1"/></svg>',
    "cloud-lightning": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 16.326A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 .5 8.973"/><path d="m13 12-3 5h4l-3 5"/></svg>',
    "cloud-fog": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 17H7"/><path d="M17 21H9"/></svg>',
    "cloud-snow": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#0EA5E9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M8 15h.01"/><path d="M8 19h.01"/><path d="M12 17h.01"/><path d="M12 21h.01"/><path d="M16 15h.01"/><path d="M16 19h.01"/></svg>',
    "wind": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/><path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>',
    "cloud-moon": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.188 8.5A6 6 0 0 1 16 4a9 9 0 0 1 3 8.358"/><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>',
    "thermometer": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/></svg>',
    "umbrella": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12a10.06 10.06 0 0 0-20 0Z"/><path d="M12 12v8a2 2 0 0 0 4 0"/><path d="M12 2v1"/></svg>',
    "bell": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>',
    "map-pin": '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "chevron-down": '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="18" x2="20" y2="18"/></svg>',
    "x": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    "chevron-left": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>',
    "download": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
}

# -------------------------------------------------------------------
# DYNAMIC WEATHER HELPER WITH COMPLETE LUCIDE REACT ICONS
# -------------------------------------------------------------------
def get_weather_icon(condition_str: str, hour: int = 8) -> str:
    """Returns the corresponding Lucide SVG according to dynamic weather condition & time."""
    if not condition_str:
        return ICONS["cloud-sun"]
    c = str(condition_str).lower().strip()
    is_night = hour < 6 or hour >= 19
    
    if "thunder" in c or "storm" in c or "lightning" in c or "squall" in c:
        return ICONS["cloud-lightning"]
    elif "snow" in c or "sleet" in c or "hail" in c or "ice" in c or "blizzard" in c:
        return ICONS["cloud-snow"]
    elif "drizzle" in c:
        return ICONS["cloud-drizzle"]
    elif "rain" in c or "shower" in c:
        return ICONS["cloud-rain"]
    elif "fog" in c or "haze" in c or "smoke" in c or "mist" in c or "dust" in c:
        return ICONS["cloud-fog"]
    elif "wind" in c or "breeze" in c or "gale" in c:
        return ICONS["wind"]
    elif "clear" in c or "sunny" in c or "fair" in c:
        return ICONS["moon"] if is_night else ICONS["sun"]
    elif "partly" in c or "scattered" in c or "few" in c:
        return ICONS["cloud-moon"] if is_night else ICONS["cloud-sun"]
    elif "cloud" in c or "overcast" in c:
        return ICONS["cloudy"] if "overcast" in c else ICONS["cloud"]
    else:
        return ICONS["cloud-moon"] if is_night else ICONS["cloud-sun"]

def get_current_weather():
    """Fetches real-time / latest telemetry weather data or falls back gracefully."""
    data_feed = api_get("/api/traffic", {"limit": 1})
    if data_feed and len(data_feed) > 0:
        latest = data_feed[-1]
        raw_weather = latest.get("weather", "Partly Cloudy")
        temp = latest.get("temperature_c", 29)
        if isinstance(temp, (int, float)):
            temp_str = f"{int(round(temp))}°C"
        else:
            temp_str = "29°C"
            
        weather_title = raw_weather.capitalize() if raw_weather else "Partly Cloudy"
        if weather_title.lower() == "clear":
            weather_desc = "Clear Skies"
        elif weather_title.lower() == "rain":
            weather_desc = "Rainy Showers"
        else:
            weather_desc = weather_title
            
        now = datetime.now()
        date_str = now.strftime("%a, %d %b %Y")
        time_str = now.strftime("%I:%M %p")
        hour = now.hour
            
        return {
            "location": "Hyderabad, India",
            "condition": weather_desc,
            "temp": temp_str,
            "date": date_str,
            "time": time_str,
            "hour": hour
        }
        
    now = datetime.now()
    return {
        "location": "Hyderabad, India",
        "condition": "Partly Cloudy",
        "temp": "29°C",
        "date": now.strftime("%a, %d %b %Y"),
        "time": now.strftime("%I:%M %p"),
        "hour": now.hour
    }

# -------------------------------------------------------------------
# 5. RENDER SIDEBAR COMPONENT (LIGHT MODE & GEIST SANS)
# -------------------------------------------------------------------
def render_sidebar():
    weather_info = get_current_weather()
    weather_icon_svg = get_weather_icon(weather_info["condition"], weather_info.get("hour", 8))

    nav_structure = [
        {"type": "single", "name": "Dashboard", "icon": "dashboard"},
        {
            "type": "group", "title": "MAIN",
            "items": [
                {"name": "Live Traffic", "icon": "activity"},
                {"name": "Traffic Prediction", "icon": "trending-up"},
                {"name": "Route Advisor", "icon": "navigation"},
                {"name": "Incidents", "icon": "alert-triangle"},
                {"name": "Reports", "icon": "file-text"},
            ]
        },
        {
            "type": "group", "title": "DATA",
            "items": [
                {"name": "History & Trends", "icon": "clock"},
                {"name": "Data Insights", "icon": "bar-chart-2"},
            ]
        },
        {
            "type": "group", "title": "SETTINGS",
            "items": [
                {"name": "Settings", "icon": "settings"},
                {"name": "Help & Support", "icon": "help-circle"},
            ]
        }
    ]

    nav_html = ""
    for sec in nav_structure:
        if sec["type"] == "single":
            is_active = " active" if page_clean == sec["name"] else ""
            nav_html += f"""
            <a href="{nav_url(sec['name'])}" class="nav-link-item{is_active}" target="_self" onclick="if(window.innerWidth<=992&&window.closeTrafforaSidebar)window.closeTrafforaSidebar();">
                {ICONS[sec['icon']]}
                <span>{sec['name']}</span>
            </a>
            """
        else:
            nav_html += f'<div class="nav-section-title">{sec["title"]}</div>'
            for it in sec["items"]:
                is_active = " active" if page_clean == it["name"] else ""
                nav_html += f"""
                <a href="{nav_url(it['name'])}" class="nav-link-item{is_active}" target="_self" onclick="if(window.innerWidth<=992&&window.closeTrafforaSidebar)window.closeTrafforaSidebar();">
                    {ICONS[it['icon']]}
                    <span>{it['name']}</span>
                </a>
                """

    sidebar_markup = f"""
    <div id="sidebarBackdrop" class="sidebar-overlay-backdrop" onclick="if(window.closeTrafforaSidebar){{window.closeTrafforaSidebar();}}else{{var s=document.getElementById('trafforaSidebar'),b=document.getElementById('sidebarBackdrop');if(s)s.classList.remove('mobile-open');if(b)b.classList.remove('active');}}"></div>
    <aside id="trafforaSidebar" class="traffora-sidebar">
        <div>
            <!-- BRAND LOGO (LUCIDE LAYERS) & CLOSE/COLLAPSE BUTTON -->
            <div class="sidebar-top">
                <div class="sidebar-brand-wrapper">
                    <div class="traffora-logo-icon">
                        {ICONS['layers']}
                    </div>
                    <div class="logo-text-col">
                        <span class="logo-brand-title">Traffora</span>
                        <span class="logo-tagline">Smart Traffic. Better Tomorrow.</span>
                    </div>
                </div>
                <button type="button" class="sidebar-close-btn" id="trafforaSidebarCloseBtn" onclick="if(window.toggleTrafforaSidebar){{window.toggleTrafforaSidebar();}}else{{var s=document.getElementById('trafforaSidebar'),b=document.getElementById('sidebarBackdrop'),m=document.querySelector('section[data-testid=stMain]');if(s){{if(window.innerWidth<=992){{s.classList.remove('mobile-open');if(b)b.classList.remove('active');}}else{{s.classList.add('collapsed');if(m)m.classList.add('sidebar-collapsed');}}}}}}" title="Close / Collapse Sidebar" aria-label="Close sidebar">
                    {ICONS['x']}
                </button>
            </div>

            <!-- NAVIGATION ITEMS -->
            <div class="sidebar-nav-container">
                {nav_html}
            </div>
        </div>

        <!-- SIDEBAR WEATHER CARD (DYNAMIC REAL-TIME DATA & LUCIDE WEATHER ICONS) -->
        <div class="sidebar-bottom">
            <div class="sidebar-weather-card" title="Real-time Weather Telemetry: {weather_info['condition']}">
                <div class="weather-header">
                    <span class="weather-location">{weather_info['location']}</span>
                    <span class="weather-icon-svg">{weather_icon_svg}</span>
                </div>
                <div class="weather-body">
                    <span class="weather-temp">{weather_info['temp']}</span>
                    <span class="weather-desc">{weather_info['condition']}</span>
                </div>
                <div class="weather-footer">
                    <span>{weather_info['date']}</span>
                    <span>{weather_info['time']}</span>
                </div>
            </div>
        </div>
    </aside>
    """
    render_html(sidebar_markup)

# -------------------------------------------------------------------
# 6. RENDER TOP HEADER COMPONENT (LIGHT MODE)
# -------------------------------------------------------------------
def render_header():
    now = datetime.now()
    header_date_str = now.strftime("%d %b %Y")

    header_markup = f"""
    <header class="traffora-top-header">
        <div class="header-left">
            <button type="button" class="header-hamburger-btn" id="trafforaHamburgerBtn" onclick="if(window.toggleTrafforaSidebar){{window.toggleTrafforaSidebar();}}else{{var s=document.getElementById('trafforaSidebar'),b=document.getElementById('sidebarBackdrop'),m=document.querySelector('section[data-testid=stMain]')||document.querySelector('.main')||document.body;if(s){{if(window.innerWidth<=992){{var o=s.classList.toggle('mobile-open');if(b)b.classList.toggle('active',o);}}else{{var c=s.classList.toggle('collapsed');if(m)m.classList.toggle('sidebar-collapsed',c);try{{localStorage.setItem('tf_sidebar_pref',c?'collapsed':'open');}}catch(e){{}}}}}}}}" title="Toggle Sidebar" aria-label="Toggle navigation">
                {ICONS['menu']}
            </button>
        </div>

        <div class="header-right">
            <!-- LOCATION SELECTOR -->
            <div class="header-pill-dropdown" onclick="alert('Current operational zone: Hyderabad Central & Metropolitan Area')">
                {ICONS['map-pin']}
                <span>Hyderabad</span>
                {ICONS['chevron-down']}
            </div>

            <!-- DATE SELECTOR (DYNAMIC REAL-TIME DATE) -->
            <div class="header-pill-dropdown date-pill" title="Select Date (Live Dynamic Telemetry)" style="position:relative;cursor:pointer;">
                {ICONS['calendar']}
                <span id="headerDateDisplay">{header_date_str}</span>
                {ICONS['chevron-down']}
                <input type="date" id="headerDatePicker" value="{now.strftime('%Y-%m-%d')}" style="position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:pointer;z-index:10;" onchange="if(window.onHeaderDateChanged)window.onHeaderDateChanged(this.value);" />
            </div>

            <!-- NOTIFICATIONS -->
            <div class="notification-btn" title="1 Active Traffic Alert" onclick="alert('Active Alert: Congestion surge predicted near HITEC City & Madhapur in +1 Hour.')">
                {ICONS['bell']}
                <span class="notification-badge">1</span>
            </div>

            <!-- USER PROFILE -->
            <div class="user-profile-widget" onclick="alert('Traffora Admin: Command Center Privileges Enabled')">
                <div class="user-avatar-circle">
                    TA
                    <span class="avatar-online-dot"></span>
                </div>
                <div class="user-text-col">
                    <span class="user-name">Traffora Admin</span>
                    <span class="user-role">Administrator</span>
                </div>
                {ICONS['chevron-down']}
            </div>
        </div>
    </header>
    """
    render_html(header_markup)

# -------------------------------------------------------------------
# 6.5 STANDALONE LEAFLET LIGHT-MODE MAP IFRAME GENERATOR
# (100% Free OpenStreetMap & CartoDB Positron - Zero API Key Needed)
# -------------------------------------------------------------------
def get_hyderabad_light_map_iframe():
    map_inner_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        html, body, #map { width: 100%; height: 100%; background: #F8FAFC; overflow: hidden; }
        
        .map-control-top-right {
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 1000;
        }
        .map-view-dropdown {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            color: #1E293B;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            user-select: none;
            transition: all 0.15s ease;
        }
        .map-view-dropdown:hover {
            background: #F1F5F9;
            border-color: #CBD5E1;
        }

        .map-zoom-controls {
            position: absolute;
            top: 54px;
            right: 14px;
            display: flex;
            flex-direction: column;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
            z-index: 1000;
            overflow: hidden;
        }
        .map-zoom-btn {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: transparent;
            border: none;
            border-bottom: 1px solid #E2E8F0;
            font-size: 16px;
            color: #1E293B;
            cursor: pointer;
            transition: background 0.15s ease;
        }
        .map-zoom-btn:last-child { border-bottom: none; }
        .map-zoom-btn:hover { background: #F1F5F9; }

        .map-legend-box {
            position: absolute;
            bottom: 14px;
            left: 14px;
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(8px);
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 7px 14px;
            display: flex;
            align-items: center;
            gap: 14px;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.07);
            user-select: none;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 600;
            color: #475569;
        }
        .legend-line {
            width: 14px;
            height: 3.5px;
            border-radius: 2px;
        }
        .legend-line.smooth { background: #16A34A; }
        .legend-line.moderate { background: #F59E0B; }
        .legend-line.heavy { background: #EF4444; }
        .legend-line.nodata { background: #94A3B8; }

        .incident-marker {
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .incident-marker:hover { transform: scale(1.25); }
        .incident-triangle-svg {
            width: 26px;
            height: 26px;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.25));
        }
        .incident-pulse {
            position: absolute;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            animation: incPulse 2s infinite;
            pointer-events: none;
        }
        .incident-marker.red .incident-pulse { background: rgba(239, 68, 68, 0.35); }
        .incident-marker.orange .incident-pulse { background: rgba(245, 158, 11, 0.35); }
        @keyframes incPulse {
            0% { transform: scale(0.6); opacity: 1; }
            100% { transform: scale(1.9); opacity: 0; }
        }

        .hub-marker {
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .hub-circle {
            width: 22px;
            height: 22px;
            background: #2563EB;
            border: 2px solid #FFFFFF;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 10px rgba(37, 99, 235, 0.6);
            color: #FFFFFF;
        }
        .hub-radar {
            position: absolute;
            width: 36px;
            height: 36px;
            border: 1.5px solid rgba(37, 99, 235, 0.5);
            border-radius: 50%;
            animation: hubWave 2.5s infinite;
        }
        @keyframes hubWave {
            0% { transform: scale(0.5); opacity: 1; }
            100% { transform: scale(2.2); opacity: 0; }
        }

        .area-label span {
            font-size: 11px;
            font-weight: 700;
            color: #1E293B;
            text-shadow: 0 0 4px #FFFFFF, 0 0 8px #FFFFFF, 0 1px 2px #FFFFFF;
            white-space: nowrap;
        }

        .leaflet-popup-content-wrapper {
            background: #FFFFFF;
            color: #1E293B;
            border-radius: 8px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12);
        }
        .leaflet-popup-content {
            margin: 10px 12px;
            font-size: 12px;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <div id="map"></div>

    <div class="map-control-top-right">
        <div class="map-view-dropdown" onclick="cycleLayer()" id="layerBtn">
            <span id="layerName">Road View</span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
    </div>

    <div class="map-zoom-controls">
        <button class="map-zoom-btn" onclick="map.zoomIn()" title="Zoom In">+</button>
        <button class="map-zoom-btn" onclick="map.zoomOut()" title="Zoom Out">−</button>
        <button class="map-zoom-btn" onclick="map.flyTo([17.4120, 78.4480], 11.5, {duration: 0.8})" title="Recenter">⌖</button>
    </div>

    <div class="map-legend-box">
        <div class="legend-item"><span class="legend-line smooth"></span><span>Smooth</span></div>
        <div class="legend-item"><span class="legend-line moderate"></span><span>Moderate</span></div>
        <div class="legend-item"><span class="legend-line heavy"></span><span>Heavy</span></div>
        <div class="legend-item"><span class="legend-line nodata"></span><span>No Data</span></div>
    </div>

    <script>
        var map = L.map('map', {
            center: [17.4120, 78.4480],
            zoom: 12,
            zoomControl: false,
            attributionControl: false
        });

        // 100% Free Tile Layers with ZERO API Keys & NO Watermarks
        var layers = [
            { name: 'Road View', layer: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }) },
            { name: 'Light Canvas', layer: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', { maxZoom: 16 }) },
            { name: 'OpenStreetMap', layer: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }) },
            { name: 'Satellite View', layer: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18 }) }
        ];

        var curIdx = 0;
        layers[0].layer.addTo(map);

        function cycleLayer() {
            map.removeLayer(layers[curIdx].layer);
            curIdx = (curIdx + 1) % layers.length;
            layers[curIdx].layer.addTo(map);
            document.getElementById('layerName').innerText = layers[curIdx].name;
        }

        // Real Hyderabad Arterial Highways
        var corridors = [
            { name: "Miyapur → Kukatpally → Begumpet (NH 65)", pts: [[17.4968, 78.3548], [17.4880, 78.3800], [17.4849, 78.4138], [17.4650, 78.4280], [17.4480, 78.4400], [17.4375, 78.4482], [17.4440, 78.4680]], color: "#EF4444", status: "Heavy (72%)", speed: "20.1 km/h" },
            { name: "HITEC City → Madhapur → Banjara Hills", pts: [[17.4699, 78.3578], [17.4474, 78.3762], [17.4483, 78.3915], [17.4380, 78.4010], [17.4319, 78.4073], [17.4200, 78.4200], [17.4156, 78.4350], [17.4280, 78.4520], [17.4440, 78.4680]], color: "#EF4444", status: "Bottleneck (78%)", speed: "18.2 km/h" },
            { name: "Begumpet → Tank Bund → Koti", pts: [[17.4440, 78.4680], [17.4250, 78.4750], [17.4100, 78.4790], [17.3950, 78.4830], [17.3850, 78.4867]], color: "#EF4444", status: "Heavy (61%)", speed: "22.5 km/h" },
            { name: "Begumpet → Paradise → Secunderabad", pts: [[17.4440, 78.4680], [17.4428, 78.4872], [17.4399, 78.4983]], color: "#F59E0B", status: "Moderate (61%)", speed: "26.8 km/h" },
            { name: "Paradise → Tarnaka → Uppal", pts: [[17.4428, 78.4872], [17.4350, 78.5080], [17.4270, 78.5350], [17.4150, 78.5500], [17.4018, 78.5602]], color: "#16A34A", status: "Smooth", speed: "42.0 km/h" },
            { name: "Uppal → Nagole → LB Nagar", pts: [[17.4018, 78.5602], [17.3820, 78.5620], [17.3600, 78.5580], [17.3457, 78.5522]], color: "#16A34A", status: "Smooth", speed: "45.2 km/h" },
            { name: "LB Nagar → Dilsukhnagar → Koti", pts: [[17.3457, 78.5522], [17.3600, 78.5380], [17.3688, 78.5247], [17.3750, 78.5050], [17.3850, 78.4867]], color: "#F59E0B", status: "Moderate (53%)", speed: "24.0 km/h" },
            { name: "Koti → Mehdipatnam", pts: [[17.3850, 78.4867], [17.3900, 78.4650], [17.3916, 78.4385]], color: "#F59E0B", status: "Moderate (48%)", speed: "25.3 km/h" },
            { name: "Mehdipatnam → Gachibowli", pts: [[17.3916, 78.4385], [17.4000, 78.4120], [17.4150, 78.3850], [17.4300, 78.3650], [17.4401, 78.3489]], color: "#16A34A", status: "Smooth", speed: "38.5 km/h" },
            { name: "Gachibowli → HITEC City", pts: [[17.4401, 78.3489], [17.4430, 78.3620], [17.4474, 78.3762]], color: "#16A34A", status: "Smooth", speed: "41.0 km/h" },
            { name: "Outer Ring Road (ORR Expressway)", pts: [[17.4401, 78.3489], [17.4180, 78.3460], [17.3600, 78.3700], [17.3190, 78.4050], [17.2600, 78.4300], [17.2300, 78.4900], [17.2500, 78.5500], [17.3000, 78.5900], [17.3457, 78.5522], [17.4018, 78.5602], [17.4600, 78.5800], [17.5200, 78.5200], [17.5100, 78.4300], [17.4968, 78.3548], [17.4401, 78.3489]], color: "#16A34A", status: "Expressway Smooth", speed: "80.0 km/h" }
        ];

        corridors.forEach(function(c) {
            L.polyline(c.pts, { color: '#FFFFFF', weight: 7, opacity: 0.95, lineCap: 'round' }).addTo(map);
            var p = L.polyline(c.pts, { color: c.color, weight: 4, opacity: 0.95, lineCap: 'round' }).addTo(map);
            p.bindPopup("<b>" + c.name + "</b><br>Status: <b>" + c.status + "</b><br>Speed: " + c.speed);
        });

        // Incidents
        var incidents = [
            { pos: [17.4350, 78.3450], col: "#EF4444", title: "Minor Accident", desc: "Reported near Gachibowli Flyover" },
            { pos: [17.4483, 78.3915], col: "#F59E0B", title: "Road Work", desc: "Work in progress on Madhapur Main Road" },
            { pos: [17.4375, 78.4482], col: "#EF4444", title: "Heavy Traffic", desc: "Signal issue at Ameerpet Junction" },
            { pos: [17.4018, 78.5602], col: "#EF4444", title: "Congestion", desc: "Backup near Uppal Corridor" }
        ];

        incidents.forEach(function(inc) {
            var html = '<div class="incident-marker ' + (inc.col === '#EF4444' ? 'red' : 'orange') + '">' +
                '<div class="incident-pulse"></div>' +
                '<svg class="incident-triangle-svg" viewBox="0 0 24 24"><polygon points="12,2 2,22 22,22" fill="' + inc.col + '" stroke="#FFFFFF" stroke-width="2"/><text x="12" y="19" fill="#FFFFFF" font-size="12" font-weight="900" text-anchor="middle">!</text></svg>' +
                '</div>';
            var icon = L.divIcon({ html: html, className: '', iconSize: [28, 28], iconAnchor: [14, 14] });
            L.marker(inc.pos, { icon: icon }).addTo(map).bindPopup("<b>" + inc.title + "</b><br>" + inc.desc);
        });

        // Hub Pin
        var hubHtml = '<div class="hub-marker"><div class="hub-radar"></div><div class="hub-circle"><svg viewBox="0 0 24 24" width="12" height="12" fill="#FFFFFF"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg></div></div>';
        var hubIcon = L.divIcon({ html: hubHtml, className: '', iconSize: [36, 36], iconAnchor: [18, 18] });
        L.marker([17.3850, 78.4867], { icon: hubIcon }).addTo(map).bindPopup("<b>Traffora Hub</b><br>Koti Command Center");

        // Area Labels
        var labels = [
            { name: "Miyapur", pos: [17.4968, 78.3548] },
            { name: "Secunderabad", pos: [17.4430, 78.5020] },
            { name: "HITEC City", pos: [17.4474, 78.3762] },
            { name: "Madhapur", pos: [17.4483, 78.3915] },
            { name: "Begumpet", pos: [17.4440, 78.4680] },
            { name: "Gachibowli", pos: [17.4350, 78.3450] },
            { name: "Paradise", pos: [17.4428, 78.4872] },
            { name: "Banjara Hills", pos: [17.4156, 78.4350] },
            { name: "Koti", pos: [17.3850, 78.4970] },
            { name: "Uppal", pos: [17.4018, 78.5602] },
            { name: "Himayatnagar", pos: [17.4027, 78.4883] },
            { name: "Kondapur", pos: [17.4699, 78.3578] },
            { name: "Mehdipatnam", pos: [17.3916, 78.4385] },
            { name: "Dilsukhnagar", pos: [17.3688, 78.5247] },
            { name: "LB Nagar", pos: [17.3457, 78.5522] }
        ];

        labels.forEach(function(l) {
            var icon = L.divIcon({ html: '<span>' + l.name + '</span>', className: 'area-label', iconSize: [80, 16], iconAnchor: [40, 8] });
            L.marker(l.pos, { icon: icon, interactive: false }).addTo(map);
        });

        // Ensure Leaflet resizes dynamically to fit parent iframe height seamlessly
        setTimeout(function() { map.invalidateSize(); }, 150);
        window.addEventListener('resize', function() { map.invalidateSize(); });
    </script>
</body>
</html>"""
    b64 = base64.b64encode(map_inner_html.encode('utf-8')).decode('ascii')
    return f'<iframe id="hyderabadMapIframe" src="data:text/html;base64,{b64}" style="width:100%;height:100%;min-height:640px;flex:1 1 auto;border:none;border-radius:12px;display:block;background:#F8FAFC;" frameborder="0"></iframe>'

# -------------------------------------------------------------------
# 7. RENDER DASHBOARD (THE PRIMARY REFERENCE UI)
# -------------------------------------------------------------------
def render_dashboard_page():
    now = datetime.now()
    if now.hour < 12:
        greeting_time = "Good Morning"
    elif now.hour < 17:
        greeting_time = "Good Afternoon"
    else:
        greeting_time = "Good Evening"

    pred_hour_1 = now + timedelta(hours=1)
    pred_alert_time_str = pred_hour_1.strftime("%I:%M %p, %d %b %Y")

    # Attempt backend fetch, fallback to dynamic reference data
    db_data = api_get("/api/dashboard")
    incidents_data = api_get("/api/incidents") or get_current_incidents()

    stats = FALLBACK_STATS.copy()
    if db_data:
        stats["total_records"] = db_data.get("total_records", 40000)

    # Top congested rows markup
    top_roads_rows_html = ""
    for road in FALLBACK_TOP_ROADS:
        badge_cls = "high" if road["level"] == "High" else "moderate"
        top_roads_rows_html += f"""
        <div class="congested-road-row">
            <div class="road-rank-name">
                <span class="road-rank-num">{road['rank']}</span>
                <span>{road['route']}</span>
            </div>
            <div class="road-badge-pct">
                <span class="congestion-badge {badge_cls}">{road['level']}</span>
                <span class="road-pct-text">{road['pct']}%</span>
            </div>
        </div>
        """

    # Recent incidents 3 cards markup
    incidents_cards_html = ""
    for inc in incidents_data[:3]:
        badge_color_cls = "red" if inc.get("severity_color") == "red" or inc.get("severity") == "High" else "orange"
        badge_label = inc.get("badge") or inc.get("type", "Incident")
        time_str = inc.get("time") or inc.get("timestamp", "08:15 AM")
        desc_text = inc.get("text") or inc.get("description", "Incident reported")
        loc_text = inc.get("location", "Hyderabad Road")

        incidents_cards_html += f"""
        <div class="incident-box">
            <div>
                <div class="incident-box-top">
                    <div class="incident-icon-badge">
                        <span style="color: {'#EF4444' if badge_color_cls == 'red' else '#F59E0B'}">{ICONS['alert-triangle']}</span>
                        <span class="incident-badge-tag {badge_color_cls}">{badge_label}</span>
                    </div>
                    <span class="incident-time-text">{time_str}</span>
                </div>
                <div class="incident-desc-text">{desc_text}</div>
                <div class="incident-loc-text">{loc_text}</div>
            </div>
            <a href="javascript:void(0)" onclick="highlightIncidentMap('{loc_text}')" class="view-on-map-btn">View on Map</a>
        </div>
        """

    # Traffic Trend Line Chart points
    trend_points = [
        (40, 150), (120, 160), (200, 115), (280, 135), (360, 110),
        (440, 125), (520, 140), (600, 115), (660, 130)
    ]

    # Clean SVG for the Traffic Trend Line Chart
    trend_points = [
        (40, 150), (120, 160), (200, 115), (280, 135), (360, 110),
        (440, 125), (520, 140), (600, 115), (660, 130)
    ]
    path_d = "M " + " L ".join([f"{x},{y}" for x, y in trend_points])
    area_d = f"{path_d} L 660,180 L 40,180 Z"

    # Assemble Entire Light Mode Dashboard
    dashboard_markup = f"""
    <div class="dashboard-content-body">
        <!-- GREETING ROW -->
        <div class="greeting-section">
            <h1 class="greeting-title">{greeting_time}, Team Traffora! 👋</h1>
            <p class="greeting-subtitle">Here's what's happening on Hyderabad roads today.</p>
        </div>

        <!-- STATISTICS CARDS (4 IN A ROW) -->
        <div class="stat-cards-grid">
            <!-- Card 1: Overall Traffic Status -->
            <div class="stat-card">
                <div class="stat-info-col">
                    <span class="stat-card-title">Overall Traffic Status</span>
                    <span class="stat-card-metric green-metric">{stats['traffic_status']}</span>
                    <span class="stat-card-desc">{stats['traffic_status_desc']}</span>
                </div>
                <div class="stat-icon-box green-box">
                    {ICONS['car']}
                </div>
            </div>

            <!-- Card 2: Average Speed -->
            <div class="stat-card">
                <div class="stat-info-col">
                    <span class="stat-card-title">Average Speed</span>
                    <span class="stat-card-metric">{stats['average_speed']}</span>
                    <span class="stat-card-desc"><span class="stat-change-red">{stats['speed_change']}</span> vs yesterday</span>
                </div>
                <div class="stat-icon-box blue-box">
                    {ICONS['gauge']}
                </div>
            </div>

            <!-- Card 3: Congested Roads -->
            <div class="stat-card">
                <div class="stat-info-col">
                    <span class="stat-card-title">Congested Roads</span>
                    <span class="stat-card-metric">{stats['congested_roads']}</span>
                    <span class="stat-card-desc"><span class="stat-change-red">{stats['congested_roads_change']}</span> vs yesterday</span>
                </div>
                <div class="stat-icon-box red-box">
                    {ICONS['traffic-jam']}
                </div>
            </div>

            <!-- Card 4: Active Incidents -->
            <div class="stat-card">
                <div class="stat-info-col">
                    <span class="stat-card-title">Active Incidents</span>
                    <span class="stat-card-metric">{stats['active_incidents']}</span>
                    <span class="stat-card-desc"><a href="{nav_url('Incidents')}" target="_self" class="stat-view-link">View all incidents</a></span>
                </div>
                <div class="stat-icon-box orange-box">
                    {ICONS['alert-triangle']}
                </div>
            </div>
        </div>

        <!-- MIDDLE GRID: MAP (LEFT) & PREDICTION + TOP CONGESTED (RIGHT) -->
        <div class="middle-grid-container">
            <!-- 1. TRAFFIC MAP CARD (DARK CARTOGRAPHIC RADAR - 1:1 REFERENCE MATCH) -->
            <!-- 1. TRAFFIC MAP CARD (LIGHT CARTOGRAPHIC HYDERABAD MAP) -->
            <div class="traffic-map-card">
                {get_hyderabad_light_map_iframe()}
            </div>

            <!-- RIGHT COLUMN: PREDICTION + TOP CONGESTED -->
            <div class="middle-right-col">
                <!-- 1. TRAFFIC PREDICTION PANEL -->
                <div class="traffic-prediction-card">
                    <div class="card-header-row">
                        <h3 class="card-title-text">Traffic Prediction</h3>
                        <a href="{nav_url('Traffic Prediction')}" target="_self" class="ai-powered-badge" title="AI Model Active · Click to view Prediction Model Engine">
                            <span class="ai-badge-dot"></span>
                            <span>AI Powered</span>
                        </a>
                    </div>

                    <!-- Location Selector -->
                    <label class="input-label-text">Select Location</label>
                    <select id="predLocationSelect" class="custom-select-box" onchange="updatePredictionState()">
                        <option value="HITEC City" selected>HITEC City</option>
                        <option value="Kukatpally">Kukatpally</option>
                        <option value="Madhapur">Madhapur</option>
                        <option value="Gachibowli">Gachibowli</option>
                        <option value="Begumpet">Begumpet</option>
                        <option value="Secunderabad">Secunderabad</option>
                    </select>

                    <!-- Time Selector -->
                    <label class="input-label-text">Select Time</label>
                    <div class="time-pills-row">
                        <div class="time-pill-btn" onclick="selectPredTime(this, 'Now')">Now</div>
                        <div class="time-pill-btn active" onclick="selectPredTime(this, '+1 Hour')">+1 Hour</div>
                        <div class="time-pill-btn" onclick="selectPredTime(this, '+2 Hour')">+2 Hour</div>
                        <div class="time-pill-btn" onclick="selectPredTime(this, '+3 Hour')">+3 Hour</div>
                    </div>

                    <!-- Prediction Result Alert Card -->
                    <div class="prediction-alert-box">
                        <div class="pred-alert-col">
                            <span id="predAlertTitle" class="pred-alert-title">High Congestion Expected</span>
                            <span id="predAlertProb" class="pred-alert-prob">78% Probability</span>
                            <span id="predAlertTime" class="pred-alert-time">At {pred_alert_time_str}</span>
                        </div>
                        <!-- Small Red Sparkline Trend SVG -->
                        <div class="pred-sparkline-svg">
                            <svg viewBox="0 0 80 38" width="100%" height="100%">
                                <defs>
                                    <linearGradient id="redGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stop-color="#EF4444" stop-opacity="0.35"/>
                                        <stop offset="100%" stop-color="#EF4444" stop-opacity="0.0"/>
                                    </linearGradient>
                                </defs>
                                <path d="M 0,30 Q 15,32 25,25 T 45,20 T 60,8 T 75,5 T 80,10 L 80,38 L 0,38 Z" fill="url(#redGrad)"/>
                                <path d="M 0,30 Q 15,32 25,25 T 45,20 T 60,8 T 75,5 T 80,10" fill="none" stroke="#EF4444" stroke-width="2.2" stroke-linecap="round"/>
                            </svg>
                        </div>
                    </div>

                    <!-- Contributing Factors -->
                    <div class="factors-title">Contributing Factors</div>
                    <div class="factors-tags-row">
                        <span class="factor-tag">Peak Hour</span>
                        <span class="factor-tag">High Vehicle Count</span>
                        <span class="factor-tag">Road Work</span>
                    </div>
                </div>

                <!-- 2. TOP CONGESTED ROADS CARD -->
                <div class="top-congested-card">
                    <div>
                        <div class="card-header-row" style="margin-bottom: 8px;">
                            <h3 class="card-title-text">Top Congested Roads</h3>
                        </div>
                        {top_roads_rows_html}
                    </div>
                    <a href="{nav_url('Live Traffic')}" target="_self" class="view-all-roads-link">
                        <span>View All Roads</span>
                        <span style="font-size: 15px;">→</span>
                    </a>
                </div>
            </div>
        </div>

        <!-- LOWER MIDDLE ROW: TRAFFIC TREND (TODAY) + CONGESTION LEVEL DONUT -->
        <div class="lower-middle-grid">
            <!-- TRAFFIC TREND (TODAY) -->
            <div class="trend-card">
                <div class="card-header-row">
                    <h3 class="card-title-text">Traffic Trend (Today)</h3>
                    <select class="chart-header-select" onchange="alert('Display metric changed: ' + this.value)">
                        <option value="Speed" selected>Speed</option>
                        <option value="Density">Density</option>
                        <option value="Volume">Volume</option>
                    </select>
                </div>

                <!-- Custom Precision SVG Line Chart -->
                <div class="trend-svg-box">
                    <svg viewBox="0 0 700 200" width="100%" height="100%" style="overflow: visible;">
                        <defs>
                            <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.25"/>
                                <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.01"/>
                            </linearGradient>
                        </defs>

                        <!-- Y-Axis Grid Lines & Labels -->
                        <line x1="40" y1="30" x2="660" y2="30" stroke="#EEF1F5" stroke-width="1"/>
                        <text x="25" y="34" font-size="11" fill="#98A2B3" text-anchor="end">60</text>

                        <line x1="40" y1="80" x2="660" y2="80" stroke="#EEF1F5" stroke-width="1"/>
                        <text x="25" y="84" font-size="11" fill="#98A2B3" text-anchor="end">40</text>

                        <line x1="40" y1="130" x2="660" y2="130" stroke="#EEF1F5" stroke-width="1"/>
                        <text x="25" y="134" font-size="11" fill="#98A2B3" text-anchor="end">20</text>

                        <line x1="40" y1="180" x2="660" y2="180" stroke="#EEF1F5" stroke-width="1"/>
                        <text x="25" y="184" font-size="11" fill="#98A2B3" text-anchor="end">0</text>

                        <!-- Area Fill Under Curve -->
                        <path d="{area_d}" fill="url(#blueGrad)"/>

                        <!-- Smooth Line Curve -->
                        <path d="{path_d}" fill="none" stroke="#3B82F6" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>

                        <!-- Highlight Dot & Tooltip at 08:00 AM (x=200, y=115) -->
                        <line x1="200" y1="30" x2="200" y2="180" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="3,3"/>
                        <circle cx="200" cy="115" r="5.5" fill="#2563EB" stroke="#FFFFFF" stroke-width="2.5"/>

                        <!-- Interactive Tooltip Box matching reference -->
                        <g transform="translate(160, 68)">
                            <rect x="0" y="0" width="80" height="38" rx="6" fill="#FFFFFF" stroke="#E5EAF0" filter="drop-shadow(0px 2px 5px rgba(0,0,0,0.08))"/>
                            <text x="40" y="16" font-size="11" font-weight="700" fill="#172033" text-anchor="middle">26.4 km/h</text>
                            <text x="40" y="29" font-size="9" font-weight="500" fill="#667085" text-anchor="middle">08:00 AM</text>
                        </g>

                        <!-- X-Axis Labels -->
                        <text x="40" y="198" font-size="10.5" fill="#98A2B3" text-anchor="middle">12 AM</text>
                        <text x="120" y="198" font-size="10.5" fill="#98A2B3" text-anchor="middle">4 AM</text>
                        <text x="200" y="198" font-size="10.5" fill="#3B82F6" font-weight="700" text-anchor="middle">8 AM</text>
                        <text x="280" y="198" font-size="10.5" fill="#98A2B3" text-anchor="middle">12 PM</text>
                        <text x="360" y="198" font-size="10.5" fill="#98A2B3" text-anchor="middle">4 PM</text>
                        <text x="440" y="198" font-size="10.5" fill="#98A2B3" text-anchor="middle">8 PM</text>
                        <text x="520" y="198" font-size="10.5" fill="#98A2B3" text-anchor="middle">12 AM</text>
                    </svg>
                </div>
            </div>

            <!-- TRAFFIC BY CONGESTION LEVEL (DONUT) -->
            <div class="donut-card">
                <div class="card-header-row">
                    <h3 class="card-title-text">Traffic by Congestion Level</h3>
                </div>

                <div class="donut-content-row">
                    <!-- Donut SVG -->
                    <div class="donut-svg-wrapper">
                        <svg viewBox="0 0 160 160" width="160" height="160">
                            <circle cx="80" cy="80" r="58" fill="none" stroke="#F1F4F8" stroke-width="18"/>
                            <circle cx="80" cy="80" r="58" fill="none" stroke="#22C55E" stroke-width="18"
                                    stroke-dasharray="243 364" stroke-dashoffset="91" transform="rotate(-90 80 80)"/>
                            <circle cx="80" cy="80" r="58" fill="none" stroke="#F59E0B" stroke-width="18"
                                    stroke-dasharray="92 364" stroke-dashoffset="-152" transform="rotate(-90 80 80)"/>
                            <circle cx="80" cy="80" r="58" fill="none" stroke="#EF4444" stroke-width="18"
                                    stroke-dasharray="30 364" stroke-dashoffset="-244" transform="rotate(-90 80 80)"/>
                        </svg>
                        <div class="donut-center-label">
                            <div class="donut-center-num">{stats['total_records']:,}</div>
                            <div class="donut-center-sub">Total Records</div>
                        </div>
                    </div>

                    <!-- Legend Items -->
                    <div class="donut-legend-col">
                        <div class="donut-legend-row">
                            <div class="donut-legend-dot-label">
                                <span class="donut-legend-dot green"></span>
                                <span>Low (Smooth)</span>
                            </div>
                            <span class="donut-legend-pct">{stats['congestion']['low_pct']}%</span>
                        </div>
                        <div class="donut-legend-row">
                            <div class="donut-legend-dot-label">
                                <span class="donut-legend-dot orange"></span>
                                <span>Moderate</span>
                            </div>
                            <span class="donut-legend-pct">{stats['congestion']['mod_pct']}%</span>
                        </div>
                        <div class="donut-legend-row">
                            <div class="donut-legend-dot-label">
                                <span class="donut-legend-dot red"></span>
                                <span>High (Heavy)</span>
                            </div>
                            <span class="donut-legend-pct">{stats['congestion']['high_pct']}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- BOTTOM ROW: RECENT INCIDENTS + QUICK ACTIONS -->
        <div class="bottom-grid-container">
            <!-- RECENT INCIDENTS -->
            <div class="recent-incidents-card">
                <div class="card-header-row">
                    <h3 class="card-title-text">Recent Incidents</h3>
                    <select class="chart-header-select" onchange="alert('Filter incidents by: ' + this.value)">
                        <option value="View All" selected>View All</option>
                        <option value="Accidents">Accidents</option>
                        <option value="Road Work">Road Work</option>
                    </select>
                </div>
                <!-- 3 Incident Cards Grid -->
                <div class="incidents-tri-grid">
                    {incidents_cards_html}
                </div>
            </div>

            <!-- QUICK ACTIONS -->
            <div class="quick-actions-card">
                <div class="card-header-row">
                    <h3 class="card-title-text">Quick Actions</h3>
                </div>
                <div class="quick-actions-col">
                    <!-- Action 1: Route Advisor -->
                    <a href="{nav_url('Route Advisor')}" target="_self" class="quick-action-item">
                        <div class="quick-action-icon green">
                            {ICONS['navigation']}
                        </div>
                        <div class="quick-action-text-col">
                            <span class="quick-action-title">Route Advisor</span>
                            <span class="quick-action-subtitle">Find Best Route</span>
                        </div>
                    </a>

                    <!-- Action 2: Report Incident -->
                    <div class="quick-action-item" onclick="openReportIncidentModal()">
                        <div class="quick-action-icon red">
                            {ICONS['alert-triangle']}
                        </div>
                        <div class="quick-action-text-col">
                            <span class="quick-action-title">Report Incident</span>
                            <span class="quick-action-subtitle">Help Others</span>
                        </div>
                    </div>

                    <!-- Action 3: Download Report -->
                    <div class="quick-action-item" onclick="downloadTrafficReportCSV()">
                        <div class="quick-action-icon blue">
                            {ICONS['download']}
                        </div>
                        <div class="quick-action-text-col">
                            <span class="quick-action-title">Download Report</span>
                            <span class="quick-action-subtitle">CSV / PDF</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    render_html(dashboard_markup)

# -------------------------------------------------------------------
# 8. SUBPAGES (SAME LIGHT MODE THEME, GEIST SANS, NO STREAMLIT WIDGETS)
# -------------------------------------------------------------------
def render_subpage(page_name):
    # Common subpage wrapper
    render_html(f"""
    <div class="dashboard-content-body">
        <div class="greeting-section">
            <h1 class="greeting-title">{page_name}</h1>
            <p class="greeting-subtitle">Traffora Traffic Command Center · Hyderabad Operations System</p>
        </div>
    """)

    if page_name == "Live Traffic":
        render_html(f"""
        <div style="background:#FFFFFF;border:1px solid #E5EAF0;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <h3 style="font-size:16px;font-weight:600;margin:0;">Metropolitan Live Telemetry & Node Feeds</h3>
                <span class="ai-powered-badge"><span class="ai-badge-dot"></span>Live Sensor Grid Active</span>
            </div>
            <p style="font-size:13px;color:#667085;margin-bottom:16px;">Displaying 16 monitored metropolitan nodes across Hyderabad Central, Cyberabad & Secunderabad.</p>
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:12px;">
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px;">
                    <div style="font-weight:600;font-size:14px;color:#172033;">HITEC City Junction</div>
                    <div style="font-size:12px;color:#EF4444;margin-top:4px;font-weight:600;">High Density · 18.2 km/h</div>
                    <div style="font-size:11px;color:#64748B;margin-top:2px;">Signal Cycle: +15s green applied</div>
                </div>
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px;">
                    <div style="font-weight:600;font-size:14px;color:#172033;">Gachibowli Outer Ring</div>
                    <div style="font-size:12px;color:#16A34A;margin-top:4px;font-weight:600;">Smooth Flow · 58.4 km/h</div>
                    <div style="font-size:11px;color:#64748B;margin-top:2px;">All 6 lanes free moving</div>
                </div>
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px;">
                    <div style="font-weight:600;font-size:14px;color:#172033;">Ameerpet Metro Hub</div>
                    <div style="font-size:12px;color:#F59E0B;margin-top:4px;font-weight:600;">Moderate Traffic · 22.5 km/h</div>
                    <div style="font-size:11px;color:#64748B;margin-top:2px;">Traffic police marshals on site</div>
                </div>
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px;">
                    <div style="font-weight:600;font-size:14px;color:#172033;">Secunderabad Station Rd</div>
                    <div style="font-size:12px;color:#16A34A;margin-top:4px;font-weight:600;">Optimal Flow · 34.1 km/h</div>
                    <div style="font-size:11px;color:#64748B;margin-top:2px;">Clear visibility · Zero incidents</div>
                </div>
            </div>
            <div style="margin-top:20px;">
                <a href="{nav_url('Dashboard')}" style="font-size:13px;font-weight:600;color:#2563EB;text-decoration:none;">← Return to Main Dashboard</a>
            </div>
        </div>
        """)

    elif page_name == "Traffic Prediction":
        render_html(f"""
        <div style="background:#FFFFFF;border:1px solid #E5EAF0;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <h3 style="font-size:16px;font-weight:600;margin:0;">AI Congestion Prediction & Simulation Engine</h3>
                <span class="ai-powered-badge"><span class="ai-badge-dot"></span>Machine Learning Model Active</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                <div>
                    <label class="input-label-text">Select Simulated Corridor</label>
                    <select class="custom-select-box" id="simLocation">
                        <option value="HITEC City">HITEC City → Madhapur</option>
                        <option value="Kukatpally">Kukatpally → Miyapur</option>
                        <option value="Ameerpet">Ameerpet → Begumpet</option>
                        <option value="LB Nagar">LB Nagar → Uppal</option>
                    </select>
                    <label class="input-label-text">Estimated Vehicle Count</label>
                    <input type="number" id="simVehicles" value="480" style="width:100%;border:1px solid #DDE3EA;border-radius:8px;padding:8px 12px;font-size:13px;margin-bottom:14px;outline:none;">
                    <label class="input-label-text">Peak Hour Condition</label>
                    <select class="custom-select-box" id="simPeak">
                        <option value="1" selected>Yes (Morning / Evening Peak)</option>
                        <option value="0">No (Off-Peak Hour)</option>
                    </select>
                    <button onclick="runAiPredictionSimulation()" style="width:100%;background:#3347A8;color:#FFFFFF;border:none;border-radius:8px;padding:10px 14px;font-size:13px;font-weight:600;cursor:pointer;">Run Model Inference →</button>
                </div>
                <div id="simResultCard" style="background:#FFF7F7;border:1px solid #F2B8B8;border-radius:10px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;">
                    <div>
                        <div style="font-size:15px;font-weight:700;color:#DC2626;">High Congestion Expected</div>
                        <div style="font-size:12px;color:#667085;margin-top:4px;">Confidence: <b>78.4%</b> · Delay Index: <b>+16 mins</b></div>
                        <p style="font-size:12.5px;color:#172033;margin-top:12px;line-height:1.5;">
                            <b>Model Inference:</b> Bottleneck detected on arterial cyber-corridor due to concurrent office rush and junction convergence.
                        </p>
                    </div>
                    <div style="border-top:1px solid #F2B8B8;padding-top:10px;font-size:11.5px;color:#991B1B;">
                        Recommended Action: Extend green clearance window at Mindspace rotary.
                    </div>
                </div>
            </div>
            <div style="margin-top:20px;">
                <a href="{nav_url('Dashboard')}" style="font-size:13px;font-weight:600;color:#2563EB;text-decoration:none;">← Return to Main Dashboard</a>
            </div>
        </div>
        """)

    elif page_name == "Route Advisor":
        render_html(f"""
        <div style="background:#FFFFFF;border:1px solid #E5EAF0;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <h3 style="font-size:16px;font-weight:600;margin:0;">Intelligent Route Optimizer & Delay Mitigation</h3>
                <span class="ai-powered-badge"><span class="ai-badge-dot"></span>Real-Time Routing</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                <div style="background:#EAF8EF;border:1px solid #BBF7D0;border-radius:10px;padding:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:700;color:#16A34A;font-size:14px;">Option A: Via Hafeezpet (Fastest)</span>
                        <span style="font-weight:700;color:#16A34A;font-size:13px;">22 mins · 9.4 km</span>
                    </div>
                    <p style="font-size:12.5px;color:#15803D;margin-top:8px;margin-bottom:0;">
                        Smooth traffic flow · 0 reported incidents · Average corridor speed 36 km/h.
                    </p>
                </div>
                <div style="background:#FFF7E6;border:1px solid #FDE68A;border-radius:10px;padding:16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:700;color:#D97706;font-size:14px;">Option B: Via Kukatpally Main Rd</span>
                        <span style="font-weight:700;color:#D97706;font-size:13px;">37 mins · 11.2 km</span>
                    </div>
                    <p style="font-size:12.5px;color:#B45309;margin-top:8px;margin-bottom:0;">
                        Heavy congestion near Y-Junction · +15 min delay reported.
                    </p>
                </div>
            </div>
            <div style="margin-top:20px;">
                <a href="{nav_url('Dashboard')}" style="font-size:13px;font-weight:600;color:#2563EB;text-decoration:none;">← Return to Main Dashboard</a>
            </div>
        </div>
        """)

    elif page_name == "Incidents":
        inc_rows = "".join([f"""
        <tr style="border-bottom:1px solid #EEF1F5;font-size:13px;">
            <td style="padding:12px 10px;font-weight:600;">#{inc['id']}</td>
            <td style="padding:12px 10px;">{inc['time']}</td>
            <td style="padding:12px 10px;font-weight:600;color:#172033;">{inc['location']}</td>
            <td style="padding:12px 10px;"><span class="incident-badge-tag {inc['severity_color']}">{inc['badge']}</span></td>
            <td style="padding:12px 10px;color:#475569;">{inc['text']}</td>
            <td style="padding:12px 10px;"><span style="color:#16A34A;font-weight:600;font-size:12px;">● Active</span></td>
        </tr>
        """ for inc in FALLBACK_INCIDENTS])

        render_html(f"""
        <div style="background:#FFFFFF;border:1px solid #E5EAF0;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <h3 style="font-size:16px;font-weight:600;margin:0;">Incident Dispatch & Management Center</h3>
                <button onclick="openReportIncidentModal()" style="background:#3347A8;color:#FFFFFF;border:none;border-radius:8px;padding:8px 14px;font-size:12.5px;font-weight:600;cursor:pointer;">+ Report New Incident</button>
            </div>
            <table style="width:100%;border-collapse:collapse;text-align:left;">
                <thead>
                    <tr style="border-bottom:2px solid #E5EAF0;font-size:11px;color:#667085;text-transform:uppercase;">
                        <th style="padding:8px 10px;">ID</th>
                        <th style="padding:8px 10px;">Time</th>
                        <th style="padding:8px 10px;">Location</th>
                        <th style="padding:8px 10px;">Type</th>
                        <th style="padding:8px 10px;">Description</th>
                        <th style="padding:8px 10px;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {inc_rows}
                </tbody>
            </table>
            <div style="margin-top:20px;">
                <a href="{nav_url('Dashboard')}" style="font-size:13px;font-weight:600;color:#2563EB;text-decoration:none;">← Return to Main Dashboard</a>
            </div>
        </div>
        """)

    else:
        render_html(f"""
        <div style="background:#FFFFFF;border:1px solid #E5EAF0;border-radius:12px;padding:32px;text-align:center;box-shadow:0 2px 8px rgba(15,23,42,0.05);">
            <div style="width:48px;height:48px;border-radius:12px;background:#EEF2FF;color:#3347A8;display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;">
                {ICONS['bar-chart-2']}
            </div>
            <h3 style="font-size:18px;font-weight:600;margin:0 0 6px 0;color:#172033;">{page_name}</h3>
            <p style="font-size:13px;color:#667085;max-width:500px;margin:0 auto 18px auto;">
                This module is integrated with the Traffora backend service and styled in pure Light Mode using Geist Sans typography.
            </p>
            <a href="{nav_url('Dashboard')}" style="background:#3347A8;color:#FFFFFF;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;text-decoration:none;display:inline-block;">← Return to Dashboard</a>
        </div>
        """)

    render_html("</div>")

# -------------------------------------------------------------------
# 9. REPORT INCIDENT MODAL & CLIENT-SIDE SCRIPTING
# -------------------------------------------------------------------
incident_modal_html = """
<div id="reportIncidentModal" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,0.45);z-index:99999;align-items:center;justify-content:center;">
    <div style="background:#FFFFFF;border:1px solid #E5EAF0;border-radius:12px;width:90%;max-width:440px;padding:24px;box-shadow:0 10px 25px rgba(15,23,42,0.15);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="margin:0;font-size:16px;font-weight:600;color:#172033;">Report Traffic Incident</h3>
            <span onclick="closeReportIncidentModal()" style="cursor:pointer;font-size:18px;color:#667085;font-weight:600;">✕</span>
        </div>
        <label class="input-label-text">Incident Type</label>
        <select id="modalIncType" class="custom-select-box">
            <option value="Accident">Accident</option>
            <option value="Road Work">Road Work</option>
            <option value="Heavy Traffic">Heavy Traffic / Congestion</option>
            <option value="Signal Failure">Traffic Signal Issue</option>
        </select>
        <label class="input-label-text">Location</label>
        <input type="text" id="modalIncLoc" placeholder="e.g. Near Cyber Towers, HITEC City" style="width:100%;border:1px solid #DDE3EA;border-radius:8px;padding:8px 12px;font-size:13px;margin-bottom:12px;outline:none;">
        <label class="input-label-text">Description</label>
        <textarea id="modalIncDesc" placeholder="Describe the traffic situation..." rows="3" style="width:100%;border:1px solid #DDE3EA;border-radius:8px;padding:8px 12px;font-size:13px;margin-bottom:16px;outline:none;resize:none;"></textarea>
        <div style="display:flex;justify-content:flex-end;gap:10px;">
            <button onclick="closeReportIncidentModal()" style="background:#FFFFFF;border:1px solid #E5EAF0;border-radius:8px;padding:8px 14px;font-size:12.5px;color:#475569;cursor:pointer;">Cancel</button>
            <button onclick="submitIncidentReport()" style="background:#3347A8;border:none;border-radius:8px;padding:8px 16px;font-size:12.5px;color:#FFFFFF;font-weight:600;cursor:pointer;">Submit Incident</button>
        </div>
    </div>
</div>
"""

raw_client_js = """
window.toggleTrafforaSidebar = function() {
    var s = document.getElementById('trafforaSidebar');
    var b = document.getElementById('sidebarBackdrop');
    var m = document.querySelector('section[data-testid="stMain"]') || document.querySelector('.main') || document.querySelector('.stApp') || document.body;
    if (!s) return;
    if (window.innerWidth <= 992) {
        var o = s.classList.toggle('mobile-open');
        if (b) b.classList.toggle('active', o);
    } else {
        var c = s.classList.toggle('collapsed');
        if (m) m.classList.toggle('sidebar-collapsed', c);
        try { localStorage.setItem('tf_sidebar_pref', c ? 'collapsed' : 'open'); } catch(e){}
    }
};

window.closeTrafforaSidebar = function() {
    var s = document.getElementById('trafforaSidebar');
    var b = document.getElementById('sidebarBackdrop');
    var m = document.querySelector('section[data-testid="stMain"]') || document.querySelector('.main') || document.querySelector('.stApp') || document.body;
    if (!s) return;
    if (window.innerWidth <= 992) {
        s.classList.remove('mobile-open');
        if (b) b.classList.remove('active');
    } else {
        s.classList.add('collapsed');
        if (m) m.classList.add('sidebar-collapsed');
        try { localStorage.setItem('tf_sidebar_pref', 'collapsed'); } catch(e){}
    }
};

window.openTrafforaSidebar = function() {
    var s = document.getElementById('trafforaSidebar');
    var b = document.getElementById('sidebarBackdrop');
    var m = document.querySelector('section[data-testid="stMain"]') || document.querySelector('.main') || document.querySelector('.stApp') || document.body;
    if (!s) return;
    if (window.innerWidth <= 992) {
        s.classList.add('mobile-open');
        if (b) b.classList.add('active');
    } else {
        s.classList.remove('collapsed');
        if (m) m.classList.remove('sidebar-collapsed');
        try { localStorage.setItem('tf_sidebar_pref', 'open'); } catch(e){}
    }
};

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        if (window.closeTrafforaSidebar) window.closeTrafforaSidebar();
    }
});

try {
    if (window.innerWidth > 992 && localStorage.getItem('tf_sidebar_pref') === 'collapsed') {
        var s = document.getElementById('trafforaSidebar');
        var m = document.querySelector('section[data-testid="stMain"]');
        if (s) s.classList.add('collapsed');
        if (m) m.classList.add('sidebar-collapsed');
    }
} catch(e){}

window.formatDynamicPredTime = function(offsetHours) {
    var picker = document.getElementById('headerDatePicker');
    var baseDate = new Date();
    if (picker && picker.value) {
        var parts = picker.value.split('-');
        if (parts.length === 3) {
            baseDate.setFullYear(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
        }
    }
    var d = new Date(baseDate.getTime());
    var now = new Date();
    d.setHours(now.getHours() + offsetHours);
    d.setMinutes(now.getMinutes());
    
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var hours = d.getHours();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? (hours < 10 ? '0' + hours : hours) : 12;
    var minutes = d.getMinutes() < 10 ? '0' + d.getMinutes() : d.getMinutes();
    var day = d.getDate() < 10 ? '0' + d.getDate() : d.getDate();
    var month = months[d.getMonth()];
    var year = d.getFullYear();
    return 'At ' + hours + ':' + minutes + ' ' + ampm + ', ' + day + ' ' + month + ' ' + year;
};

window.onHeaderDateChanged = function(val) {
    if (!val) return;
    var parts = val.split('-');
    if (parts.length === 3) {
        var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        var y = parts[0];
        var m = months[parseInt(parts[1], 10) - 1];
        var d = parts[2];
        var formatted = d + ' ' + m + ' ' + y;
        var disp = document.getElementById('headerDateDisplay');
        if (disp) disp.innerText = formatted;
        
        var activeBtn = document.querySelector('.time-pill-btn.active');
        var timeStr = activeBtn ? activeBtn.innerText.trim() : '+1 Hour';
        var offset = 1;
        if (timeStr === 'Now') offset = 0;
        else if (timeStr === '+2 Hour') offset = 2;
        else if (timeStr === '+3 Hour') offset = 3;
        
        var timeEl = document.getElementById('predAlertTime');
        if (timeEl) timeEl.innerText = window.formatDynamicPredTime(offset);
    }
};

window.selectPredTime = function(el, timeStr) {
    document.querySelectorAll('.time-pill-btn').forEach(function(btn){ btn.classList.remove('active'); });
    el.classList.add('active');
    
    var titleEl = document.getElementById('predAlertTitle');
    var probEl = document.getElementById('predAlertProb');
    var timeEl = document.getElementById('predAlertTime');

    if (timeStr === 'Now') {
        if (titleEl) titleEl.innerText = 'Moderate Traffic Flowing';
        if (probEl) probEl.innerText = '62% Probability';
        if (timeEl) timeEl.innerText = window.formatDynamicPredTime(0);
    } else if (timeStr === '+1 Hour') {
        if (titleEl) titleEl.innerText = 'High Congestion Expected';
        if (probEl) probEl.innerText = '78% Probability';
        if (timeEl) timeEl.innerText = window.formatDynamicPredTime(1);
    } else if (timeStr === '+2 Hour') {
        if (titleEl) titleEl.innerText = 'Peak Bottleneck Alert';
        if (probEl) probEl.innerText = '84% Probability';
        if (timeEl) timeEl.innerText = window.formatDynamicPredTime(2);
    } else {
        if (titleEl) titleEl.innerText = 'Traffic Normalizing Expected';
        if (probEl) probEl.innerText = '55% Probability';
        if (timeEl) timeEl.innerText = window.formatDynamicPredTime(3);
    }
};

window.updatePredictionState = function() {
    var sel = document.getElementById('predLocationSelect');
    if (!sel) return;
    var loc = sel.value;
    var titleEl = document.getElementById('predAlertTitle');
    if (titleEl) {
        titleEl.innerText = 'High Congestion at ' + loc;
    }
};

window.currentMapLayerIndex = 0;
window.mapLayers = [
    { name: 'Road View', url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', maxZoom: 19, subdomains: 'abcd' },
    { name: 'OpenStreetMap', url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', maxZoom: 19, subdomains: 'abc' },
    { name: 'Satellite View', url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', maxZoom: 18, subdomains: 'abc' }
];

window.initHyderabadLeafletMap = function() {
    var container = document.getElementById('hyderabadLeafletMap');
    if (!container) return;
    
    if (window.hydLeafletMapInstance) {
        try { window.hydLeafletMapInstance.invalidateSize(); } catch(e){}
        return;
    }

    if (typeof L === 'undefined') {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);

        var script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = function() {
            setTimeout(window.initHyderabadLeafletMap, 50);
        };
        document.head.appendChild(script);
        return;
    }

    // Clean existing leaflet container state if any
    container._leaflet_id = null;

    var map = L.map('hyderabadLeafletMap', {
        center: [17.4120, 78.4480],
        zoom: 11.5,
        zoomControl: false,
        attributionControl: false
    });
    window.hydLeafletMapInstance = map;

    // CartoDB Dark Matter tile layer
    window.currentTileLayer = L.tileLayer(window.mapLayers[0].url, {
        maxZoom: window.mapLayers[0].maxZoom,
        subdomains: window.mapLayers[0].subdomains
    }).addTo(map);

    // Hyderabad Arterial Corridors (Curved Highway Geometry matching Image 1 & 2)
    var corridors = [
        // 1. NH 65: Miyapur -> Kukatpally -> Ameerpet -> Begumpet (Red Heavy 72%)
        {
            name: "Miyapur → Kukatpally → Begumpet (NH 65)",
            pts: [[17.4968, 78.3548], [17.4880, 78.3800], [17.4849, 78.4138], [17.4650, 78.4280], [17.4480, 78.4400], [17.4375, 78.4482], [17.4440, 78.4680]],
            color: "#EF4444", status: "Heavy Congestion (72%)", speed: "20.1 km/h"
        },
        // 2. Cyberabad: Kondapur -> HITEC City -> Madhapur -> Jubilee Hills -> Banjara Hills -> Begumpet (Red Heavy 78%)
        {
            name: "HITEC City → Madhapur → Banjara Hills",
            pts: [[17.4699, 78.3578], [17.4474, 78.3762], [17.4483, 78.3915], [17.4380, 78.4010], [17.4319, 78.4073], [17.4200, 78.4200], [17.4156, 78.4350], [17.4280, 78.4520], [17.4440, 78.4680]],
            color: "#EF4444", status: "Severe Bottleneck (78%)", speed: "18.2 km/h"
        },
        // 3. Central Arterial: Begumpet -> Tank Bund -> Koti (Red Heavy 61%)
        {
            name: "Begumpet → Tank Bund → Koti",
            pts: [[17.4440, 78.4680], [17.4250, 78.4750], [17.4100, 78.4790], [17.3950, 78.4830], [17.3850, 78.4867]],
            color: "#EF4444", status: "Heavy Traffic (61%)", speed: "22.5 km/h"
        },
        // 4. Northeast: Begumpet -> Paradise -> Secunderabad (Orange Moderate 61%)
        {
            name: "Begumpet → Paradise → Secunderabad",
            pts: [[17.4440, 78.4680], [17.4428, 78.4872], [17.4399, 78.4983]],
            color: "#F59E0B", status: "Moderate (61%)", speed: "26.8 km/h"
        },
        // 5. Eastern Arterial: Paradise -> Tarnaka -> Uppal (Green Smooth)
        {
            name: "Paradise → Tarnaka → Uppal",
            pts: [[17.4428, 78.4872], [17.4350, 78.5080], [17.4270, 78.5350], [17.4150, 78.5500], [17.4018, 78.5602]],
            color: "#10B981", status: "Smooth Flow", speed: "42.0 km/h"
        },
        // 6. Ring Road East: Uppal -> Nagole -> LB Nagar (Green Smooth)
        {
            name: "Uppal → Nagole → LB Nagar",
            pts: [[17.4018, 78.5602], [17.3820, 78.5620], [17.3600, 78.5580], [17.3457, 78.5522]],
            color: "#10B981", status: "Smooth Flow", speed: "45.2 km/h"
        },
        // 7. Southeast Arterial: LB Nagar -> Dilsukhnagar -> Koti (Orange Moderate 53%)
        {
            name: "LB Nagar → Dilsukhnagar → Koti",
            pts: [[17.3457, 78.5522], [17.3600, 78.5380], [17.3688, 78.5247], [17.3750, 78.5050], [17.3850, 78.4867]],
            color: "#F59E0B", status: "Moderate (53%)", speed: "24.0 km/h"
        },
        // 8. Southwest: Koti -> Mehdipatnam (Orange Moderate 48%)
        {
            name: "Koti → Mehdipatnam",
            pts: [[17.3850, 78.4867], [17.3900, 78.4650], [17.3916, 78.4385]],
            color: "#F59E0B", status: "Moderate (48%)", speed: "25.3 km/h"
        },
        // 9. West Link: Mehdipatnam -> Tolichowki -> Gachibowli (Green Smooth)
        {
            name: "Mehdipatnam → Gachibowli",
            pts: [[17.3916, 78.4385], [17.4000, 78.4120], [17.4150, 78.3850], [17.4300, 78.3650], [17.4401, 78.3489]],
            color: "#10B981", status: "Smooth Flow", speed: "38.5 km/h"
        },
        // 10. Financial District Link: Gachibowli -> HITEC City (Green Smooth)
        {
            name: "Gachibowli → HITEC City",
            pts: [[17.4401, 78.3489], [17.4430, 78.3620], [17.4474, 78.3762]],
            color: "#10B981", status: "Smooth Flow", speed: "41.0 km/h"
        },
        // 11. Outer Ring Road (ORR Expressway) Loop (Green Smooth)
        {
            name: "Outer Ring Road (ORR Expressway)",
            pts: [
                [17.4401, 78.3489], [17.4180, 78.3460], [17.3600, 78.3700], [17.3190, 78.4050],
                [17.2600, 78.4300], [17.2300, 78.4900], [17.2500, 78.5500], [17.3000, 78.5900],
                [17.3457, 78.5522], [17.4018, 78.5602], [17.4600, 78.5800], [17.5200, 78.5200],
                [17.5100, 78.4300], [17.4968, 78.3548], [17.4401, 78.3489]
            ],
            color: "#10B981", status: "Expressway Flow Normal", speed: "80.0 km/h"
        }
    ];

    corridors.forEach(function(c) {
        // Crisp White Casing Underlay for contrast on light mode maps
        L.polyline(c.pts, {
            color: '#FFFFFF',
            weight: 7,
            opacity: 0.95,
            lineCap: 'round',
            lineJoin: 'round'
        }).addTo(map);

        // Core Traffic Polyline
        var poly = L.polyline(c.pts, {
            color: c.color,
            weight: 4,
            opacity: 0.95,
            lineCap: 'round',
            lineJoin: 'round'
        }).addTo(map);

        poly.bindPopup("<b>" + c.name + "</b><br>Traffic Flow: <span style='color:" + c.color + ";font-weight:700;'>" + c.status + "</span><br>Average Speed: <b>" + c.speed + "</b>");
    });

    // Real Incident Warning Triangles matching Image 1 & 2
    window.incidentMarkers = {};
    var incidents = [
        {
            id: "Gachibowli",
            locName: "Near Gachibowli Flyover",
            pos: [17.4350, 78.3450],
            color: "#EF4444",
            type: "Accident Alert",
            desc: "Minor accident reported on Outer Ring Road near Gachibowli Flyover"
        },
        {
            id: "Madhapur",
            locName: "Madhapur Main Road",
            pos: [17.4483, 78.3915],
            color: "#F59E0B",
            type: "Road Work Alert",
            desc: "Road work in progress on Madhapur Main Road"
        },
        {
            id: "Ameerpet",
            locName: "Ameerpet Junction",
            pos: [17.4375, 78.4482],
            color: "#EF4444",
            type: "Heavy Traffic Alert",
            desc: "Heavy traffic due to signal issue at Ameerpet Junction"
        },
        {
            id: "Uppal",
            locName: "Uppal",
            pos: [17.4018, 78.5602],
            color: "#EF4444",
            type: "Congestion Bottleneck",
            desc: "Severe vehicle backup near Uppal Circle"
        }
    ];

    incidents.forEach(function(inc) {
        var markerHtml = '<div class="leaflet-incident-marker ' + (inc.color === '#EF4444' ? 'red' : 'orange') + '">' +
            '<div class="incident-marker-pulse"></div>' +
            '<svg class="incident-triangle-icon" viewBox="0 0 24 24">' +
                '<polygon points="12,2 2,22 22,22" fill="' + inc.color + '" stroke="#FFFFFF" stroke-width="2"/>' +
                '<text x="12" y="19" fill="#FFFFFF" font-size="12" font-weight="900" text-anchor="middle">!</text>' +
            '</svg>' +
        '</div>';

        var icon = L.divIcon({
            html: markerHtml,
            className: 'custom-leaflet-icon',
            iconSize: [28, 28],
            iconAnchor: [14, 14]
        });

        var m = L.marker(inc.pos, { icon: icon }).addTo(map);
        m.bindPopup("<b>" + inc.type + "</b><br>" + inc.desc + "<br><span style='color:#94A3B8;font-size:11px;'>" + inc.locName + "</span>");
        window.incidentMarkers[inc.locName] = m;
        window.incidentMarkers[inc.id] = m;
    });

    // Central Command Hub Pin at Koti
    var hubHtml = '<div class="leaflet-hub-marker">' +
        '<div class="hub-radar-ring"></div>' +
        '<div class="hub-center-circle">' +
            '<svg viewBox="0 0 24 24" width="12" height="12" fill="#FFFFFF"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>' +
        '</div>' +
    '</div>';

    var hubIcon = L.divIcon({
        html: hubHtml,
        className: 'custom-hub-icon',
        iconSize: [36, 36],
        iconAnchor: [18, 18]
    });
    L.marker([17.3850, 78.4867], { icon: hubIcon }).addTo(map).bindPopup("<b>Traffora Central Radar Hub</b><br>Koti Operations Center");

    // Clear Location Labels matching Image 1 & 2
    var labels = [
        { name: "Miyapur", pos: [17.4968, 78.3548] },
        { name: "Secunderabad", pos: [17.4430, 78.5020] },
        { name: "HITEC City", pos: [17.4474, 78.3762] },
        { name: "Madhapur", pos: [17.4483, 78.3915] },
        { name: "Begumpet", pos: [17.4440, 78.4680] },
        { name: "Gachibowli Hills", pos: [17.4350, 78.3450] },
        { name: "Paradise", pos: [17.4428, 78.4872] },
        { name: "Banjara Hills", pos: [17.4156, 78.4350] },
        { name: "Koti", pos: [17.3850, 78.4970] },
        { name: "Uppal", pos: [17.4018, 78.5602] },
        { name: "Himayatnagar", pos: [17.4027, 78.4883] },
        { name: "Kondapur", pos: [17.4699, 78.3578] },
        { name: "Mehdipatnam", pos: [17.3916, 78.4385] },
        { name: "Dilsukhnagar", pos: [17.3688, 78.5247] },
        { name: "LB Nagar", pos: [17.3457, 78.5522] }
    ];

    labels.forEach(function(l) {
        var labelIcon = L.divIcon({
            html: '<span>' + l.name + '</span>',
            className: 'leaflet-area-label',
            iconSize: [80, 16],
            iconAnchor: [40, 8]
        });
        L.marker(l.pos, { icon: labelIcon, interactive: false }).addTo(map);
    });

    setTimeout(function() {
        map.invalidateSize();
    }, 300);
};

window.zoomTrafficMap = function(dir) {
    if (window.hydLeafletMapInstance) {
        if (dir > 0) window.hydLeafletMapInstance.zoomIn();
        else window.hydLeafletMapInstance.zoomOut();
    }
};

window.resetTrafficMap = function() {
    if (window.hydLeafletMapInstance) {
        window.hydLeafletMapInstance.flyTo([17.4120, 78.4480], 11.5, { duration: 1.0 });
    }
};

window.cycleMapLayer = function() {
    if (!window.hydLeafletMapInstance) return;
    window.currentMapLayerIndex = ((window.currentMapLayerIndex || 0) + 1) % window.mapLayers.length;
    var layerInfo = window.mapLayers[window.currentMapLayerIndex];
    
    if (window.currentTileLayer) {
        window.hydLeafletMapInstance.removeLayer(window.currentTileLayer);
    }
    
    window.currentTileLayer = L.tileLayer(layerInfo.url, {
        maxZoom: layerInfo.maxZoom,
        subdomains: layerInfo.subdomains
    }).addTo(window.hydLeafletMapInstance);
    
    var labelEl = document.getElementById('currentMapViewLabel');
    if (labelEl) labelEl.innerText = layerInfo.name;
};

window.highlightIncidentMap = function(locText) {
    if (!window.hydLeafletMapInstance) {
        alert('Focusing radar on incident location: ' + locText);
        return;
    }
    
    var target = null;
    if (window.incidentMarkers) {
        for (var k in window.incidentMarkers) {
            if (locText.toLowerCase().indexOf(k.toLowerCase()) !== -1 || k.toLowerCase().indexOf(locText.toLowerCase()) !== -1) {
                target = window.incidentMarkers[k];
                break;
            }
        }
    }
    
    if (target) {
        var ll = target.getLatLng();
        window.hydLeafletMapInstance.flyTo(ll, 14, { duration: 1.2 });
        setTimeout(function() { target.openPopup(); }, 1300);
    } else {
        window.hydLeafletMapInstance.flyTo([17.4120, 78.4480], 12.5, { duration: 1.0 });
    }
};

// Automatically boot Leaflet dark map
setTimeout(function() {
    if (window.initHyderabadLeafletMap) window.initHyderabadLeafletMap();
}, 250);

window.openReportIncidentModal = function() {
    var m = document.getElementById('reportIncidentModal');
    if (m) m.style.display = 'flex';
};

window.closeReportIncidentModal = function() {
    var m = document.getElementById('reportIncidentModal');
    if (m) m.style.display = 'none';
};

window.submitIncidentReport = function() {
    var type = document.getElementById('modalIncType').value;
    var loc = document.getElementById('modalIncLoc').value || 'Hyderabad City';
    var desc = document.getElementById('modalIncDesc').value || 'Reported by Traffic Admin';

    fetch('http://127.0.0.1:8000/api/incidents', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type, location: loc, description: desc, severity: 'High'})
    }).catch(function(){});

    alert('Incident reported successfully: ' + type + ' at ' + loc);
    window.closeReportIncidentModal();
};

window.downloadTrafficReportCSV = function() {
    var now = new Date();
    var picker = document.getElementById('headerDatePicker');
    var todayStr = (picker && picker.value) ? picker.value : now.toISOString().slice(0, 10);
    var rows = [
        ["Date", "Corridor", "Speed_kmph", "Congestion_Level", "Probability"],
        [todayStr, "HITEC City -> Madhapur", "18.2", "High", "78%"],
        [todayStr, "Kukatpally -> Miyapur", "20.1", "High", "72%"],
        [todayStr, "Ameerpet -> Begumpet", "22.5", "Moderate", "61%"],
        [todayStr, "LB Nagar -> Uppal", "24.0", "Moderate", "53%"],
        [todayStr, "Banjara Hills -> Jubilee Hills", "25.3", "Moderate", "48%"],
        [todayStr, "Overall Network Average", "26.4", "Moderate", "N/A"]
    ];
    var csvContent = "data:text/csv;charset=utf-8," + rows.map(function(e){ return e.join(","); }).join("\\n");
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "Traffora_Hyderabad_Traffic_Report_" + todayStr + ".csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
"""

b64_script = base64.b64encode(raw_client_js.encode("utf-8")).decode("ascii")

client_scripts = f"""
<img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='1' height='1'></svg>" 
     onload="(function(){{try{{eval(atob('{b64_script}'));}}catch(e){{console.error(e);}}}})()" 
     style="position:fixed;top:-100px;left:-100px;width:1px;height:1px;opacity:0.001;pointer-events:none;" />
"""

# -------------------------------------------------------------------
# 10. MAIN ROUTING DISPATCHER
# -------------------------------------------------------------------
render_sidebar()
render_header()

if page_clean == "Dashboard":
    render_dashboard_page()
else:
    render_subpage(page_clean)

# Render modal and client scripts at bottom of document
render_html(f"{incident_modal_html}{client_scripts}")