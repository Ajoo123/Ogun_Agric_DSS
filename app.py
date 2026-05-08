import streamlit as st
import rasterio
import os
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ogun State Agric-Pro DSS", layout="wide", page_icon="🇳🇬")

# --- MINISTRY-GRADE STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8faf8; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
        border-left: 6px solid #2e7d32; 
    }
    .report-header { 
        color: #1b5e20; 
        font-family: 'Segoe UI', sans-serif; 
        border-bottom: 3px solid #2e7d32; 
        padding-bottom: 10px; 
        margin-bottom: 25px; 
        font-weight: bold;
    }
    .guide-card {
        background-color: #e8f5e9;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #c8e6c9;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- COMPREHENSIVE CROP DATABASE ---
CROP_DB = {
    "Beans (Cowpea)": {"type": "Legume", "season": "Apr-May / Aug-Sept", "harvest": "3 months", "profit_margin": 0.48, "advice": "Excellent for nitrogen fixation. Use improved varieties like IT99K."},
    "Cocoa": {"type": "Cash Crop", "season": "Oct-Mar (Harvest)", "harvest": "3-5 years", "profit_margin": 0.78, "advice": "Ministry Standard: Ensure 3m x 3m spacing and provide nursery shade."},
    "Cashew": {"type": "Cash Crop", "season": "Jan-Mar", "harvest": "3-4 years", "profit_margin": 0.65, "advice": "High tolerance for dry spells in Northern Ogun regions."},
    "Cassava": {"type": "Root/Tuber", "season": "Mar-June", "harvest": "10-12 months", "profit_margin": 0.45, "advice": "Process quickly after harvest to maintain high starch quality."},
    "Maize": {"type": "Cereal", "season": "Mar-Apr (Early) / Aug (Late)", "harvest": "3-4 months", "profit_margin": 0.38, "advice": "Apply NPK 15-15-15 at planting for maximum yield."},
    "Oil Palm": {"type": "Cash Crop", "season": "Year-round", "harvest": "3-4 years", "profit_margin": 0.82, "advice": "Gold mine for Ogun investors. Requires consistent moisture in year 1."},
    "Tomato": {"type": "Vegetable", "season": "Oct-Feb (Dry Season)", "harvest": "3 months", "profit_margin": 0.62, "advice": "High demand in Lagos/Abeokuta markets. Requires irrigation."},
    "Plantain": {"type": "Fruit", "season": "Year-round", "harvest": "10-12 months", "profit_margin": 0.50, "advice": "Use organic mulch and poultry droppings for bigger bunches."},
    "Pepper (Rodo)": {"type": "Vegetable", "season": "Year-round", "harvest": "3-4 months", "profit_margin": 0.55, "advice": "Harvest weekly to encourage new fruit growth."}
}

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Ogun_State.svg/2560px-Flag_of_Ogun_State.svg.png", width=120)
st.sidebar.title("System Menu")
app_mode = st.sidebar.radio("Navigate", ["Live Analysis Dashboard", "Ministry User Guide"])

if app_mode == "Ministry User Guide":
    st.markdown("<h1 class='report-header'>📖 Official Operations Manual</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class="guide-card">
    <h3>Standard Operating Procedure (SOP)</h3>
    <ol>
        <li><b>Coordinate Verification:</b> Input UTM Zone 31N Easting and Northing. If coordinates fall outside the state boundary, the system will lock for data integrity.</li>
        <li><b>Soil Intelligence:</b> The system cross-references GPS pings with rasterized Nitrogen and Clay data.</li>
        <li><b>Economic Modeling:</b> Profit is calculated based on 2026 standardized production costs (N280,000/Ha) and crop-specific margins.</li>
        <li><b>Reporting:</b> Always download the Excel report for physical filing at the Ministry of Agriculture.</li>
    </ol>
    <hr>
    <i>Certification: This DSS is designed for precision agricultural planning in Ogun State.</i>
    </div>
    """, unsafe_allow_html=True)

else:
    # --- DASHBOARD PAGE ---
    st.markdown("<h1 style='text-align: center; color: #1b5e20;'>OGUN STATE AGRICULTURAL DSS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Precision Site Suitability & Profitability Portal</p>", unsafe_allow_html=True)

    # --- ROW 1: INPUT PARAMETERS ---
    with st.container():
        st.markdown("<h3 class='report-header'>1. Farm Parameters</h3>", unsafe_allow_html=True)
        i1, i2, i3, i4 = st.columns(4)
        with i1: utm_e = st.number_input("UTM Easting (X)", value=552000.0)
        with i2: utm_n = st.number_input("UTM Northing (Y)", value=790000.0)
        with i3: land_size = st.number_input("Land Area (Hectares)", min_value=0.1, value=1.0, step=0.5)
        with i4: selected_crop = st.selectbox("Select Target Crop", list(CROP_DB.keys()))

    # --- CALCULATION TRIGGER ---
    if st.button("📊 GENERATE OFFICIAL ANALYTIC REPORT", use_container_width=True):
        # 1. GEOFENCE SECURITY (Ogun Boundaries)
        if not (450000 <= utm_e <= 635000 and 700000 <= utm_n <= 870000):
            st.error("🚨 BOUNDARY VIOLATION: Coordinate detected outside Ogun State. Process terminated.")
        else:
            # 2. DATA EXTRACTION
            base_path = "raw_data/dem/"
            soil_data = {}
            files_to_check = {"Nitrogen": "ogun_nitrogen.tif", "Clay": "ogun_clay.tif", "Sand": "ogun_sand.tif"}
            
            try:
                for label, fname in files_to_check.items():
                    fpath = os.path.join(base_path, fname)
                    if os.path.exists(fpath):
                        with rasterio.open(fpath) as src:
                            val = list(src.sample([(utm_e, utm_n)]))[0][0]
                            soil_data[label] = val
                    else:
                        soil_data[label] = "N/A"

                # 3. PROFITABILITY CALCULATOR
                base_production_cost = 280000 
                profit_calc = (base_production_cost * CROP_DB[selected_crop]["profit_margin"]) * land_size

                # --- ROW 2: VISUAL INTELLIGENCE ---
                st.markdown("<h3 class='report-header'>2. Geographic & Economic Intelligence</h3>", unsafe_allow_html=True)
                v1, v2 = st.columns([1, 1])
                
                with v1:
                    st.write("🌍 **Farm Location Map**")
                    # Approximate Lat/Lon for map centering
                    m = folium.Map(location=[7.15, 3.35], zoom_start=9)
                    folium.Marker([7.15, 3.35], popup=f"Proposed {selected_crop} Farm", icon=folium.Icon(color='darkgreen')).add_to(m)
                    st_folium(m, height=350, use_container_width=True)

                with v2:
                    st.metric("Estimated Net Profit", f"₦{profit_calc:,.2f}", delta="ROI Optimized")
                    st.write(f"**Crop Type:** {CROP_DB[selected_crop]['type']}")
                    st.write(f"**Optimal Season:** {CROP_DB[selected_crop]['season']}")
                    st.write(f"**Time to Harvest:** {CROP_DB[selected_crop]['harvest']}")
                    st.success(f"📘 **Ministry Guidance:** {CROP_DB[selected_crop]['advice']}")

                # --- ROW 3: SOIL PROFILE ---
                st.markdown("<h3 class='report-header'>3. Soil Nutrient Analysis</h3>", unsafe_allow_html=True)
                s1, s2, s3 = st.columns(3)
                s1.metric("Nitrogen (N)", f"{soil_data.get('Nitrogen')} mg/kg")
                s2.metric("Clay Content", f"{soil_data.get('Clay', 0)/10 if soil_data.get('Clay') != 'N/A' else 0}%")
                s3.metric("Sand Content", f"{soil_data.get('Sand', 0)/10 if soil_data.get('Sand') != 'N/A' else 0}%")

                # --- ROW 4: EXPORT ENGINE ---
                st.markdown("<h3 class='report-header'>4. Official Data Export</h3>", unsafe_allow_html=True)
                
                # Prepare data for all formats
                report_dict = {
                    "Analysis_Date": [datetime.now().strftime("%Y-%m-%d")],
                    "UTM_X": [utm_e], "UTM_Y": [utm_n],
                    "Crop": [selected_crop], "Land_Size_Ha": [land_size],
                    "Profit_Naira": [profit_calc], "Nitrogen_Level": [soil_data.get('Nitrogen')]
                }
                df_report = pd.DataFrame(report_dict)

                e1, e2 = st.columns(2)
                
                # Excel Export
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_report.to_excel(writer, index=False, sheet_name='Ogun_Agric_Report')
                
                with e1:
                    st.download_button(
                        label="📥 Download Professional Excel Report",
                        data=excel_buffer.getvalue(),
                        file_name=f"Ogun_Report_{selected_crop}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with e2:
                    st.download_button(
                        label="📄 Download CSV Data File",
                        data=df_report.to_csv(index=False).encode('utf-8'),
                        file_name=f"Ogun_Data_{selected_crop}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Analysis failed to execute: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("Ogun State Agricultural Decision Support System v3.0 | Faculty of Engineering Deployment")