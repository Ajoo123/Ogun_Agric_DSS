import streamlit as st
import rasterio
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Ogun Agric DSS", layout="wide")
st.title("🌾 Ogun State Agricultural Decision Support System")

# 1. PATH CHECKER - This helps us find your files
target_file = "raw_data/dem/ogun_acc_SUCCESS.tif"

if not os.path.exists(target_file):
    st.error(f"❌ File not found at: {target_file}")
    st.write("Checking what files ARE available...")
    # This list everything in your folders to help us debug
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".tif"):
                st.code(f"Found file at: {os.path.join(root, file)}")
else:
    st.success("✅ Map data located! Loading...")
    
    # 2. LOAD AND DISPLAY
    with rasterio.open(target_file) as src:
        # Downsample to 10% size to avoid memory crashes
        data = src.read(1, out_shape=(1, int(src.height // 10), int(src.width // 10)))
        
        fig, ax = plt.subplots(figsize=(10, 5))
        img = ax.imshow(data, cmap='terrain')
        plt.colorbar(img, ax=ax)
        ax.set_title("Ogun State Topographic Analysis")
        st.pyplot(fig)