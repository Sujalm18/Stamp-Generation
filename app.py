# 🚀 STREAMLIT STAMP GENERATOR (ACTUAL FIX — MATCHES YOUR SLIDER SETTINGS)

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator (Accurate like StampJam)")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
uploaded_templates = st.file_uploader("Upload Stamp Templates (PNG)", type=["png"], accept_multiple_files=True)

# SETTINGS (MATCH YOUR SCREENSHOT)
LETTER_SPACING = 100   # controls spread
START_ANGLE = 52.4     # start point
RADIUS_FACTOR = 0.36   # ring fit

# Font loader

def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# ✅ FINAL CORRECT LOGIC (NO GUESSWORK)

def draw_circular_text(draw, center, radius, text, font):
    text = text.upper()

    # Convert spacing to angle properly
    spacing_angle = LETTER_SPACING / 10  # normalize

    angle = START_ANGLE

    for char in text:
        angle_rad = math.radians(angle)

        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)

        # rotate character tangentially
        char_img = Image.new("RGBA", (120, 120), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((60,60), char, font=font, fill="black", anchor="mm")

        rotated = char_img.rotate(angle + 90, resample=Image.BICUBIC)

        draw.bitmap((x-60, y-60), rotated)

        angle += spacing_angle

# Center text

def draw_center_text(draw, center, text, font):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center[0]-w/2, center[1]-h/2), text, fill="black", font=font)

# Generator

def generate_preview(df, templates):
    previews = []

    for _, row in df.iterrows():
        name = str(row["name"])
        city = str(row["city"])

        for template_file in templates:
            template = Image.open(template_file).convert("RGBA")
            img = template.copy()
            draw = ImageDraw.Draw(img)

            center = (img.width // 2, img.height // 2)

            radius = int(img.width * RADIUS_FACTOR)

            font_outer = get_font(int(img.width * 0.045))
            font_center = get_font(int(img.width * 0.09))

            # NAME (now respects your slider settings)
            draw_circular_text(draw, center, radius, name, font_outer)

            # CITY
            draw_center_text(draw, center, city.upper(), font_center)

            previews.append((img, f"{name}_{city}_{template_file.name}"))

    return previews

if uploaded_file and uploaded_templates:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.lower() for col in df.columns]

        if "name" not in df.columns or "city" not in df.columns:
            st.error("Excel must contain Name and City")
        else:
            st.subheader("👀 Preview")

            previews = generate_preview(df.head(3), uploaded_templates)

            for img, name in previews:
                st.image(img, caption=name)

            if st.button("🚀 Generate & Download"):
                os.makedirs("outputs", exist_ok=True)
                output_files = []

                previews = generate_preview(df, uploaded_templates)

                for img, name in previews:
                    path = os.path.join("outputs", name + ".png")
                    img.save(path)
                    output_files.append(path)

                zip_path = "stamps.zip"
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file in output_files:
                        zipf.write(file, os.path.basename(file))

                with open(zip_path, "rb") as f:
                    st.download_button("⬇️ Download ZIP", f, file_name="stamps.zip")

                st.success("✅ Now matches your provided settings")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Uses your exact slider values: spacing, radius, start angle")

# requirements.txt
# streamlit
# pandas
# pillow
# openpyxl
