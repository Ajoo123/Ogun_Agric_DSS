import streamlit as st
import rasterio
import os
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ogun State Agric-Elite DSS", layout="wide", page_icon="🇳🇬")

# --- INITIALIZE SESSION STATE (Memory) ---
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'farm_journal' not in st.session_state:
    st.session_state.farm_journal = []

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f1; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; border-top: 5px solid #2e7d32; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .category-header { color: #1b5e20; font-weight: bold; border-bottom: 2px solid #2e7d32; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- THE ALL-INCLUSIVE NIGERIAN CROP DATABASE ---
CROP_DB = {
    "Grains & Cereals": {
        "Maize": {"margin": 0.38, "season": "Mar-Apr / Aug", "harvest": "4 months", "advice": "Apply NPK 15-15-15."},
        "Rice": {"margin": 0.52, "season": "May-July", "harvest": "5 months", "advice": "Best for Ogun riverine lowlands."},
        "Beans (Cowpea)": {"margin": 0.48, "season": "Apr / Aug-Sept", "harvest": "3 months", "advice": "Nitrogen-fixing; improves soil."}
    },
    "Roots & Tubers": {
        "Cassava": {"margin": 0.45, "season": "Mar-June", "harvest": "12 months", "advice": "Process quickly after harvest."},
        "Yam": {"margin": 0.55, "season": "Feb-Apr", "harvest": "8 months", "advice": "Requires deep, loose loamy soil."},
        "Sweet Potato": {"margin": 0.42, "season": "May-July", "harvest": "4 months", "advice": "Grows well in sandy loam."}
    },
    "Fruits": {
        "Pineapple": {"margin": 0.58, "season": "Year-round", "harvest": "18 months", "advice": "Ogun is a leader in pineapple export."},
        "Orange (Citrus)": {"margin": 0.50, "season": "May-June", "harvest": "3 years", "advice": "Requires consistent pruning."},
        "Plantain/Banana": {"margin": 0.54, "season": "Year-round", "harvest": "11 months", "advice": "Keep in wind-protected areas."}
    },
    "Vegetables": {
        "Tomato": {"margin": 0.65, "season": "Oct-Feb", "harvest": "3 months", "advice": "High market demand in Lagos."},
        "Pepper (Rodo)": {"margin": 0.55, "season": "Year-round", "harvest": "4 months", "advice": "Harvest weekly for more yield."},
        "Ugu (Leafy)": {"margin": 0.40, "season": "Apr-Oct", "harvest": "1 month", "advice": "Fastest cash-flow crop."}
    },
    "Cash Crops": {
        "Cocoa": {"margin": 0.80, "season": "Oct-Mar", "harvest": "3-5 years", "advice": "Requires shade canopy for seedlings."},
        "Cashew": {"margin": 0.65, "season": "Jan-Mar", "harvest": "4 years", "advice": "Thrives in Northern Ogun (Yewa)."},
        "Oil Palm": {"margin": 0.85, "season": "Year-round", "harvest": "4 years", "advice": "Most profitable long-term crop."}
    }
}

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Ogun_State.svg/2560px-Flag_of_Ogun_State.svg.png", width=100)
    st.title("Admin Controls")
    
    if st.button("🧹 Clear Dashboard"):
        st.session_state.analysis_results = None
        st.rerun()
    
    st.markdown("---")
    st.subheader("📝 Saved Farm Logs")
    for log in reversed(st.session_state.farm_journal):
        st.caption(log)

# --- MAIN DASHBOARD ---
st.title("🟢 Ogun State Agricultural Intelligence Portal")
st.markdown("### Official Decision Support System for Precision Farming")

# --- STEP 1: INPUTS ---
with st.container():
    st.markdown("<h3 class='category-header'>1. Site & Crop Selection</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: utm_e = st.number_input("UTM Easting (X)", value=552000.0)
    with c2: utm_n = st.number_input("UTM Northing (Y)", value=790000.0)
    with c3: land_size = st.number_input("Land Size (Ha)", min_value=0.1, value=1.0)
    
    # Classification Logic
    cat_col1, cat_col2 = st.columns(2)
    with cat_col1:
        category = st.selectbox("Crop Category", list(CROP_DB.keys()))
    with cat_col2:
        crop = st.selectbox("Specific Crop", list(CROP_DB[category].keys()))

# --- STEP 2: ANALYSIS TRIGGER ---
if st.button("📊 GENERATE OFFICIAL SITE REPORT", use_container_width=True):
    if not (450000 <= utm_e <= 635000 and 700000 <= utm_n <= 870000):
        st.error("🚨 BOUNDARY ERROR: Site is outside Ogun State territory.")
    else:
        # DATA FETCHING
        base_path = "raw_data/dem/"
        soil = {}
        for label, fname in {"Nitrogen": "ogun_nitrogen.tif", "Clay": "ogun_clay.tif"}.items():
            path = os.path.join(base_path, fname)
            if os.path.exists(path):
                with rasterio.open(path) as src:
                    soil[label] = list(src.sample([(utm_e, utm_n)]))[0][0]
            else:
                soil[label] = 0
        
        # CALCULATION
        prof = (280000 * CROP_DB[category][crop]["margin"]) * land_size
        
        # SAVE TO MEMORY
        st.session_state.analysis_results = {
            "crop": crop, "cat": category, "prof": prof, "soil": soil,
            "e": utm_e, "n": utm_n, "size": land_size
        }

# --- STEP 3: PERSISTENT RESULTS ---
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    st.markdown("<h3 class='category-header'>2. Geographic & Economic Results</h3>", unsafe_allow_html=True)
    
    r1, r2 = st.columns([1, 1])
    with r1:
        m = folium.Map(location=[7.15, 3.35], zoom_start=9)
        folium.Marker([7.15, 3.35], popup="Proposed Farm Site", icon=folium.Icon(color='green')).add_to(m)
        st_folium(m, height=350, use_container_width=True, key="main_map")
        
    with r2:
        st.metric("Estimated Net Profit", f"₦{res['prof']:,.2f}", delta="Annualized")
        st.info(f"**Season:** {CROP_DB[res['cat']][res['crop']]['season']} | **Harvest:** {CROP_DB[res['cat']][res['crop']]['harvest']}")
        st.success(f"💡 **Expert Advice:** {CROP_DB[res['cat']][res['crop']]['advice']}")
        
        if st.button("💾 Save to Farm Journal"):
            log_entry = f"{datetime.now().strftime('%H:%M')}: Analyzed {res['crop']} on {res['size']}Ha"
            st.session_state.farm_journal.append(log_entry)
            st.toast("Report Saved to Sidebar Journal!")

    st.markdown("<h3 class='category-header'>3. Soil Nutrient Profile</h3>", unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    s1.metric("Nitrogen (N)", f"{res['soil'].get('Nitrogen')} mg/kg")
    s2.metric("Clay Content", f"{res['soil'].get('Clay', 0)/10}%")

    # --- EXPORT ---
    df = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Crop": res['crop'], "Profit": res['prof']}])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button("📥 Download Excel Report", data=buf.getvalue(), file_name="Ogun_Agric_Report.xlsx", use_container_width=True)

st.markdown("---")
st.caption("Ogun State Agric-Pro DSS v4.0 | Faculty of Engineering Deployment")