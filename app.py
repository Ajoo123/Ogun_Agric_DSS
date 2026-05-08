import streamlit as st
import rasterio
import os
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ogun State Agric-DSS", layout="wide", page_icon="🌾")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Ogun_State.svg/2560px-Flag_of_Ogun_State.svg.png", width=100)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home & Analysis", "How to Use", "About the Data"])

if page == "Home & Analysis":
    st.title("🌾 Ogun State Agricultural Decision Support System")
    st.markdown("### Precision Farming Intelligence for Nigerian Soil")

    # --- INPUT SECTION ---
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            utm_e = st.number_input("UTM Easting (X)", value=550000.0, help="E.g., 550000 for Abeokuta area")
        with col2:
            utm_n = st.number_input("UTM Northing (Y)", value=780000.0, help="E.g., 780000")
        with col3:
            current_month = st.selectbox("Current Planting Month", 
                                        ["January", "February", "March", "April", "May", "June", 
                                         "July", "August", "September", "October", "November", "December"])

    if st.button("🚀 Run Site-Specific Intelligence Report", use_container_width=True):
        base_path = "raw_data/dem/"
        # Ensure these names match your files exactly!
        files = {
            "Nitrogen": "ogun_nitrogen.tif",
            "Clay": "ogun_clay.tif",
            "Sand": "ogun_sand.tif"
        }
        
        results = {}
        
        try:
            with st.spinner("Analyzing Soil Properties..."):
                for label, filename in files.items():
                    path = os.path.join(base_path, filename)
                    if os.path.exists(path):
                        with rasterio.open(path) as src:
                            sample = list(src.sample([(utm_e, utm_n)]))
                            results[label] = sample[0][0]
                    else:
                        st.warning(f"Note: {filename} not found in {base_path}")

            if results:
                st.success(f"Analysis Complete for Coordinates: {utm_e}E, {utm_n}N")
                
                # --- RESULTS DISPLAY ---
                m1, m2, m3 = st.columns(3)
                
                # Nitrogen & Fertilizer
                n_val = results.get("Nitrogen", 0)
                with m1:
                    st.metric("Soil Nitrogen", f"{n_val} mg/kg")
                    if n_val < 50:
                        st.error("📉 LOW NITROGEN")
                        st.write("**Advice:** Apply 2 bags of Urea per hectare at week 3.")
                    else:
                        st.success("✅ HEALTHY NITROGEN")
                        st.write("**Advice:** Use standard NPK 15-15-15 schedule.")

                # Clay & Flood Risk
                clay_val = results.get("Clay", 0) / 10
                with m2:
                    st.metric("Clay Content", f"{clay_val:.1f}%")
                    if clay_val > 35:
                        st.warning("🌊 WATER RETENTION")
                        st.write("**Advice:** Best for Rice. If planting Cassava, build 40cm high ridges.")
                    else:
                        st.info("🚜 GOOD DRAINAGE")
                        st.write("**Advice:** Excellent for Maize and Yam.")

                # Sand & Management
                sand_val = results.get("Sand", 0) / 10
                with m3:
                    st.metric("Sand Content", f"{sand_val:.1f}%")
                    if sand_val > 60:
                        st.warning("☀️ HIGH EVAPORATION")
                        st.write("**Advice:** Soil dries fast. Apply mulch to conserve moisture.")
                    else:
                        st.success("🌱 BALANCED TEXTURE")
                        st.write("**Advice:** Soil has good nutrient holding capacity.")

                st.markdown("---")
                st.subheader("🗓️ Seasonal Management Plan")
                st.info(f"Based on **{current_month}** planting in Ogun State, ensure you check the local rainfall forecast before applying Nitrogen fertilizer to prevent leaching.")

        except Exception as e:
            st.error(f"GIS Error: {e}. Please ensure coordinates are valid for UTM Zone 31N.")

elif page == "How to Use":
    st.header("📖 User Guide")
    st.write("1. Get your UTM coordinates from a GPS or Google Earth (Zone 31N).")
    st.write("2. Select the month you intend to plant.")
    st.write("3. Click 'Run Analysis' to get specific fertilizer and crop advice.")

elif page == "About the Data":
    st.header("📊 Data Sources")
    st.write("Soil data provided by **ISRIC SoilGrids** (250m resolution).")
    st.write("Project developed for Ogun State Agricultural Development.")