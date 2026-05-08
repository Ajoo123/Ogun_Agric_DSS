import streamlit as st
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Ogun State Agric DSS", layout="wide")

st.title("🌾 Ogun State Agricultural Decision Support System")
st.markdown("### Flood Risk & Soil Fertility Analysis")

# Define paths to your uploaded files
# Note: These paths match your folder structure in the screenshots
data_dir = "raw_data/dem/"
acc_file = os.path.join(data_dir, "ogun_acc_SUCCESS.tif")
tpi_file = os.path.join(data_dir, "ogun_tpi_v2.tif")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Flow Accumulation (Flood Risk)")
    if os.path.exists(acc_file):
        with rasterio.open(acc_file) as src:
            fig, ax = plt.subplots()
            show(src, ax=ax, cmap='terrain')
            st.pyplot(fig)
    else:
        st.error("Flow accumulation data not found.")

with col2:
    st.subheader("Topographic Position (Soil/Landform)")
    if os.path.exists(tpi_file):
        with rasterio.open(tpi_file) as src:
            fig, ax = plt.subplots()
            show(src, ax=ax, cmap='magma')
            st.pyplot(fig)
    else:
        st.error("TPI data not found.")

st.sidebar.info("This system uses high-resolution DEM data to identify optimal farming zones in Ogun State.")