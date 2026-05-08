import streamlit as st
import rasterio
from rasterio.enums import Resampling
import matplotlib.pyplot as plt
import os

# Page Configuration
st.set_page_config(page_title="Ogun Agric DSS", layout="wide")

st.title("🌾 Ogun State Agricultural Decision Support System")
st.markdown("---")

# sidebar for navigation
st.sidebar.header("Control Panel")
layer_choice = st.sidebar.radio(
    "Select Map Layer:",
    ("Flood Risk (Flow Accumulation)", "Landform Analysis (TPI)")
)

# Helper function to load large files safely
def load_and_plot(file_path, title, colormap):
    if os.path.exists(file_path):
        with st.spinner(f'Loading {title}...'):
            with rasterio.open(file_path) as src:
                # Downsample by factor of 10 to prevent memory crashes
                data = src.read(
                    1, 
                    out_shape=(1, int(src.height // 10), int(src.width // 10)),
                    resampling=Resampling.bilinear
                )
                
                fig, ax = plt.subplots(figsize=(10, 6))
                im = ax.imshow(data, cmap=colormap)
                plt.colorbar(im, ax=ax, label='Value')
                ax.set_title(title)
                ax.axis('off')
                st.pyplot(fig)
    else:
        st.error(f"File not found: {file_path}. Please check your GitHub folder structure.")

# File Paths (Matches your 'raw_data/dem/' folder)
acc_path = "raw_data/dem/ogun_acc_SUCCESS.tif"
tpi_path = "raw_data/dem/ogun_tpi_v2.tif"

# Display Logic
if layer_choice == "Flood Risk (Flow Accumulation)":
    st.subheader("🌊 Flood Risk Identification")
    st.info("Bright blue areas indicate high water accumulation zones (potential flood paths).")
    load_and_plot(acc_path, "Ogun State Flow Accumulation", "Blues")

else:
    st.subheader("⛰️ Landform & Soil Analysis")
    st.info("This index helps identify ridges (well-drained) vs valleys (moisture-rich).")
    load_and_plot(tpi_path, "Topographic Position Index (TPI)", "terrain")

st.markdown("---")
st.caption("Developed for Ogun State Agricultural Planning | Data Source: SRTM 30m DEM")