# 🚀 STREAMLIT STAMP GENERATOR (GITHUB READY)
# Just upload this file as app.py to GitHub and deploy on Streamlit Cloud

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator")
st.write("Upload Excel file to generate stamp images")

# Upload Excel
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# Upload multiple templates
uploaded_templates = st.file_uploader("Upload Stamp Templates (PNG)", type=["png"], accept_multiple_files=True)

# Circular text function

def draw_circular_text(draw, center, radius, text, font):
    angle_step = 360 / len(text)
    for i, char in enumerate(text):
        angle = math.radians(i * angle_step - 90)
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        draw.text((x, y), char, fill="black", font=font, anchor="mm")

# Main processing
if uploaded_file and uploaded_templates:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.lower() for col in df.columns]

        if "name" not in df.columns or "city" not in df.columns:
            st.error("Excel must contain 'Name' and 'City' columns")
        else:
            os.makedirs("outputs", exist_ok=True)
            font = ImageFont.load_default()

            output_files = []

            for _, row in df.iterrows():
                name = str(row["name"]).upper()
                city = str(row["city"]).upper()

                for template_file in uploaded_templates:
                    template = Image.open(template_file).convert("RGBA")
                    img = template.copy()
                    draw = ImageDraw.Draw(img)

                    center = (img.width // 2, img.height // 2)

                    draw_circular_text(draw, center, 180, name, font)
                    draw_circular_text(draw, center, 120, city, font)

                    filename = f"{name}_{city}_{template_file.name}"
                    path = os.path.join("outputs", filename)
                    img.save(path)
                    output_files.append(path)

            # Create ZIP
            zip_path = "stamps.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in output_files:
                    zipf.write(file, os.path.basename(file))

            st.success("✅ Stamps generated successfully!")

            # Download button
            with open(zip_path, "rb") as f:
                st.download_button("⬇️ Download ZIP", f, file_name="stamps.zip")

    except Exception as e:
        st.error(str(e))

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit")


# =========================
# REQUIREMENTS.TXT
# =========================
# streamlit
# pandas
# pillow
# openpyxl
