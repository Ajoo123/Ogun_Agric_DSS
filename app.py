import streamlit as st
import rasterio
import os
import pandas as pd
from streamlit_folium import st_folium
import folium
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ogun Agric-Pro DSS", layout="wide", page_icon="🌴")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- COMPREHENSIVE NIGERIAN CROP DATABASE ---
CROP_DB = {
    # --- STAPLES ---
    "Cassava": {"type": "Root/Tuber", "season": "March-June", "harvest": "10-12 months", "profit_margin": 0.45, "advice": "Best for Gari/Lafun. Ensure timely weeding."},
    "Maize": {"type": "Cereal", "season": "March-April (Early)", "harvest": "3-4 months", "profit_margin": 0.35, "advice": "Apply Urea at week 3 and 6."},
    "Yam": {"type": "Root/Tuber", "season": "Feb-April", "harvest": "6-9 months", "profit_margin": 0.55, "advice": "Requires staking and mulching to conserve moisture."},
    "Rice": {"type": "Cereal", "season": "May-July", "harvest": "4-5 months", "profit_margin": 0.50, "advice": "Ideal for lowland regions of Ogun (e.g., Eggua)."},
    
    # --- CASH CROPS ---
    "Cocoa": {"type": "Cash Crop", "season": "Oct-March (Main Harvest)", "harvest": "3-5 years", "profit_margin": 0.75, "advice": "Requires shade during early growth. High export value."},
    "Cashew": {"type": "Cash Crop", "season": "January-March", "harvest": "3 years", "profit_margin": 0.65, "advice": "Thrives in Yewa North and drought-prone areas."},
    "Oil Palm": {"type": "Cash Crop", "season": "Year-round", "harvest": "3-4 years", "profit_margin": 0.80, "advice": "Extremely profitable long-term investment."},
    "Cashew": {"type": "Cash Crop", "season": "Jan-March", "harvest": "3-4 years", "profit_margin": 0.65, "advice": "Low maintenance once established."},

    # --- FRUITS ---
    "Pineapple": {"type": "Fruit", "season": "Year-round", "harvest": "12-18 months", "profit_margin": 0.55, "advice": "Ogun is a leader here. Ensure slightly acidic soil."},
    "Orange/Citrus": {"type": "Fruit", "season": "May-June", "harvest": "3-5 years", "profit_margin": 0.50, "advice": "Regular pruning increases fruit size."},
    "Plantain": {"type": "Fruit", "season": "Year-round", "harvest": "10-12 months", "profit_margin": 0.50, "advice": "Plant in wind-protected areas to prevent snapping."},

    # --- VEGETABLES ---
    "Tomato": {"type": "Vegetable", "season": "Oct-Feb (Irrigated)", "harvest": "3 months", "profit_margin": 0.60, "advice": "High risk, high reward. Watch for blight."},
    "Pepper (Rodo)": {"type": "Vegetable", "season": "Year-round", "harvest": "3-4 months", "profit_margin": 0.52, "advice": "Well-drained soil is non-negotiable."},
    "Ugu (Fluted Pumpkin)": {"type": "Vegetable", "season": "April-October", "harvest": "1 month", "profit_margin": 0.40, "advice": "Provides weekly cash flow for smallholders."},
}

# --- SIDEBAR: JOURNAL & NAVIGATION ---
if "journal" not in st.session_state:
    st.session_state.journal = []

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Ogun_State.svg/2560px-Flag_of_Ogun_State.svg.png", width=100)
    st.title("👨‍🌾 Farmer Tools")
    
    st.subheader("📝 Activity Log")
    new_entry = st.text_input("Enter farm activity:")
    if st.button("Save Log"):
        time_stamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.session_state.journal.append(f"{time_stamp}: {new_entry}")
    
    for entry in reversed(st.session_state.journal[-5:]): # Show last 5
        st.write(f"- {entry}")

# --- MAIN UI ---
st.title("🟢 Ogun State Agric Decision Support System")
st.markdown("### Interactive Precision Farming & Profitability Dashboard")

# --- INPUT SECTION ---
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        utm_e = st.number_input("UTM Easting (X)", value=552000.0)
    with col2:
        utm_n = st.number_input("UTM Northing (Y)", value=790000.0)
    with col3:
        land_size = st.number_input("Farmland Area (Hectares)", min_value=0.1, value=1.0)

selected_crop = st.selectbox("What do you want to plant?", list(CROP_DB.keys()))

if st.button("🚀 Run Analysis & Profitability Report", use_container_width=True):
    # 1. GEOFENCE CHECK
    # Strict Ogun State Boundary Check
    if not (450000 <= utm_e <= 635000 and 700000 <= utm_n <= 870000):
        st.error("🚨 COORDINATE OUTSIDE OGUN STATE")
        st.warning("This system is strictly calibrated for Ogun State soil. Please enter valid coordinates.")
    else:
        # 2. SOIL DATA EXTRACTION
        base_path = "raw_data/dem/"
        files = {"Nitrogen": "ogun_nitrogen.tif", "Clay": "ogun_clay.tif", "Sand": "ogun_sand.tif"}
        soil_vals = {}
        
        try:
            with st.spinner("Extracting Soil Intelligence..."):
                for label, filename in files.items():
                    path = os.path.join(base_path, filename)
                    if os.path.exists(path):
                        with rasterio.open(path) as src:
                            sample = list(src.sample([(utm_e, utm_n)]))
                            soil_vals[label] = sample[0][0]
                    else:
                        st.warning(f"Warning: {label} file not found.")

            # 3. PROFITABILITY LOGIC
            cost_per_ha = 250000 # Average cost in Naira
            roi = CROP_DB[selected_crop]["profit_margin"]
            estimated_profit = (cost_per_ha * roi) * land_size

            # --- DISPLAY REPORT ---
            st.markdown("---")
            c_left, c_right = st.columns([1, 1])

            with c_left:
                st.subheader("🌍 Map Verification")
                # Creating a preview map (Note: center is approx Abeokuta)
                m = folium.Map(location=[7.15, 3.35], zoom_start=8)
                folium.Marker([7.15, 3.35], popup="Farm Site").add_to(m)
                st_folium(m, height=300, use_container_width=True)

            with c_right:
                st.subheader("📊 Economic Forecast")
                st.metric("Potential Profit", f"₦{estimated_profit:,.2f}")
                st.write(f"**Crop Category:** {CROP_DB[selected_crop]['type']}")
                st.write(f"**Planting Season:** {CROP_DB[selected_crop]['season']}")
                st.write(f"**Maturity:** {CROP_DB[selected_crop]['harvest']}")
                st.success(f"💡 **Expert Advice:** {CROP_DB[selected_crop]['advice']}")

            st.markdown("#### 🧪 Soil Analysis Results")
            s1, s2, s3 = st.columns(3)
            s1.metric("Nitrogen Level", f"{soil_vals.get('Nitrogen', 'N/A')} mg/kg")
            s2.metric("Clay Content", f"{soil_results.get('Clay', 0)/10 if 'Clay' in soil_vals else 0}%")
            s3.metric("Sand Content", f"{soil_results.get('Sand', 0)/10 if 'Sand' in soil_vals else 0}%")

            # 4. EXPORT FEATURE
            report_data = {
                "Date": [datetime.now().strftime("%Y-%m-%d")],
                "Location_X": [utm_e], "Location_Y": [utm_n],
                "Crop": [selected_crop], "Profit_Est": [estimated_profit]
            }
            df = pd.DataFrame(report_data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Official Report", csv, "Ogun_Agric_Report.csv", "text/csv")

        except Exception as e:
            st.error(f"Analysis failed: {e}")