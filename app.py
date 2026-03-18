# 🚀 STREAMLIT STAMP GENERATOR (FINAL VERSION WITH SLIDERS 🔥)

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator (Interactive UI)")

# =========================
# 🎛️ CONTROLS (LIKE STAMPJAM)
# =========================

font_size_slider = st.slider("Font Size", 10, 100, 40)
letter_spacing_slider = st.slider("Letter Spacing", 5, 30, 12)
radius_slider = st.slider("Radius Adjust", 0.1, 0.5, 0.25)
arc_span_slider = st.slider("Arc Span (Text Width)", 60, 200, 140)
start_angle_slider = st.slider("Start Angle", -180, 180, -90)

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
uploaded_templates = st.file_uploader("Upload Stamp Templates (PNG)", type=["png"], accept_multiple_files=True)

# Font loader

def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# Circular text (TOP ARC)

def draw_circular_text(draw, center, radius, text, font):
    text = text.upper()

    arc_span = arc_span_slider

    if len(text) > 1:
        angle_step = arc_span / (len(text) - 1)
    else:
        angle_step = 0

    start_angle = start_angle_slider - arc_span / 2

    for i, char in enumerate(text):
        angle = start_angle + i * angle_step
        angle_rad = math.radians(angle)

        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)

        char_img = Image.new("RGBA", (120, 120), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((60,60), char, font=font, fill="black", anchor="mm")

        rotated = char_img.rotate(angle + 90, resample=Image.BICUBIC)

        draw.bitmap((x-60, y-60), rotated)

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

            outer = img.width * 0.44
            inner = img.width * 0.30

            base_radius = inner + (outer - inner) * radius_slider

            font_outer = get_font(font_size_slider)
            font_center = get_font(int(font_size_slider * 1.5))

            # 🔥 FINAL RADIUS FIX (accounts for font height)
            radius = int(base_radius - font_outer.size * 0.6)

            draw_circular_text(draw, center, radius, name, font_outer)
            draw_center_text(draw, center, city.upper(), font_center)

            previews.append((img, f"{name}_{city}_{template_file.name}"))

    return previews

# =========================
# 🚀 MAIN FLOW
# =========================

if uploaded_file and uploaded_templates:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.lower() for col in df.columns]

        if "name" not in df.columns or "city" not in df.columns:
            st.error("Excel must contain Name and City")
        else:
            st.subheader("👀 Live Preview")

            previews = generate_preview(df.head(2), uploaded_templates)

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

                st.success("✅ Perfect Output Generated")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Now fully interactive — adjust sliders until PERFECT 🎯")

# requirements.txt
# streamlit
# pandas
# pillow
# openpyxl
