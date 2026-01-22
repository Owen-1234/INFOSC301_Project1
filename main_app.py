import streamlit as st
import pandas as pd
import folium
import plotly.graph_objects as go
import requests
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from math import radians, cos, sin, asin, sqrt

from world_model_engine import UrbanWorldModel
from simulation_manager import SimulationManager

# --- UTILS ---
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371 * 1000

# --- CONFIG ---
DEEPSEEK_API_KEY = ""
AMAP_KEY = ""

st.set_page_config(layout="wide", page_title="UrbanRetail World Model")


st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stMetricValue"] { color: white !important; font-weight: bold; }
    [data-testid="stMetricLabel"] p { color: white !important; }
    .analysis-container { background-color: #1a1c24; padding: 20px; border-radius: 12px; border: 1px solid #333; }

    .reasoning-box { color: white !important; font-size: 14px; line-height: 1.6; margin-top: 15px; }
    .stAlert p { color: white !important; }
    .review-box { background: #262730; padding: 12px; border-radius: 8px; font-style: italic; color: #ccc !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ---
if 'virtual_shops' not in st.session_state: st.session_state.virtual_shops = []

@st.cache_data
def fetch_pois():
    url = f"https://restapi.amap.com/v3/place/text?key={AMAP_KEY}&keywords=咖啡&city=昆山&offset=45"
    r = requests.get(url).json()
    data = []
    for p in r.get('pois', []):
        lon, lat = p['location'].split(',')
        data.append({
            'Name': p['name'], 'lat': float(lat), 'lon': float(lon),
            'Rating': p.get('biz_ext', {}).get('rating', '4.2'),
            'Photo': p['photos'][0]['url'] if p.get('photos') else "https://via.placeholder.com/400x250",
            'is_virtual': False,
            'Comment': "Established market player with high brand recognition."
        })
    return pd.DataFrame(data)

if 'base_df' not in st.session_state: st.session_state.base_df = fetch_pois()
df_all = pd.concat([st.session_state.base_df, pd.DataFrame(st.session_state.virtual_shops)], ignore_index=True)

# --- UI ---
st.sidebar.title("⚙️ Simulation Tool")
enable_heat = st.sidebar.checkbox("🔥 Show Heatmap", value=False)
SimulationManager.render_sidebar()

col_map, col_panel = st.columns([2.2, 1], gap="large")

with col_map:
    m = folium.Map(location=[31.385, 120.980], zoom_start=15, tiles='cartodbpositron')
    if enable_heat: HeatMap([[r['lat'], r['lon'], 1.0] for _, r in df_all.iterrows()], radius=25).add_to(m)
    for _, row in df_all.iterrows():
        color = "#FF4B4B" if row['is_virtual'] else "#00FFAA"
        folium.CircleMarker(location=[row['lat'], row['lon']], radius=8, color=color, fill=True).add_to(m)
    map_res = st_folium(m, width="100%", height=720, key="retail_map")

with col_panel:
    point = map_res.get("last_clicked")
    marker = map_res.get("last_object_clicked")
    
    is_shop = False
    target = None
    if marker and point:
        if haversine(point['lng'], point['lat'], marker['lng'], marker['lat']) < 30:
            is_shop = True
            target = marker
    if not is_shop and point: target = point

    if target:
        df_all['dist'] = df_all.apply(lambda r: haversine(target['lng'], target['lat'], r['lon'], r['lat']), axis=1)
        selected = df_all.sort_values('dist').iloc[0]
        config = selected.get('config') if (is_shop and selected['is_virtual']) else None
        
        st.subheader(f"☕ {selected['Name']}" if is_shop else "📍 Site Analysis")

        with st.status("🧠 DeepSeek World Model Inference...", expanded=True):
            wm = UrbanWorldModel(DEEPSEEK_API_KEY)
            nearby = df_all[df_all['dist'] > 5].sort_values('dist').head(3).to_dict('records')
            res = wm.predict_urban_dynamics(f"{target['lat']:.4f},{target['lng']:.4f}", "Lunch Break", nearby, is_shop, config)

        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        if is_shop:
            st.image(selected['Photo'], use_container_width=True)
            st.markdown(f"**Market Context:**")
            st.markdown(f'<div class="review-box">"{selected.get("Comment")}"</div>', unsafe_allow_html=True)
            if selected['is_virtual']:
                st.write(f"📈 **Payback Period:** {res.get('payback_months', 0):.1f} months")
            st.write("---")
        
        m1, m2 = st.columns(2)
        m1.metric("Predicted Flow", f"{res.get('predicted_traffic')} /hr")
        m2.metric("Monthly Revenue", f"¥{res.get('est_monthly_revenue', 0):,}")


        sc = res.get('radar_scores', {"traffic": 50, "competition": 50, "brand": 50})
        fig = go.Figure(data=go.Scatterpolar(
            r=[sc['traffic'], sc['competition'], sc['brand'], sc['traffic']],
            theta=['Traffic', 'Competition', 'Brand Power', 'Traffic'],
            fill='toself', line_color='#00FFAA', fillcolor='rgba(0, 255, 170, 0.3)'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#444")),
                          height=280, margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"<div class='reasoning-box'><b>AI Reasoning:</b> {res.get('reasoning')}</div>", unsafe_allow_html=True)
        
        if 'swot' in res:
            st.write("---")
            st.markdown(f"✅ **Strength:** {res['swot'].get('strength')}")
            st.markdown(f"⚠️ **Risk:** {res['swot'].get('risk')}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Please select a shop marker or click a site on the map.")

st.caption("Developed by Shilin Ou | Urban Computing & Data Viz")
