# 🚀 STREAMLIT STAMP GENERATOR (PIXEL-PERFECT ENGINE 🔥 FINAL)

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator (Pixel Perfect)")

# 🎛️ CONTROLS
font_size = st.slider("Font Size", 10, 100, 40)
radius_adjust = st.slider("Radius Adjust", 0.1, 0.5, 0.22)
arc_span = st.slider("Arc Span", 80, 200, 140)
start_angle = st.slider("Start Angle", -180, 180, -90)

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
templates = st.file_uploader("Upload Templates", type=["png"], accept_multiple_files=True)

# Font loader

def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# ✅ TRUE BASELINE CIRCULAR TEXT ENGINE

def draw_circular_text(draw, center, radius, text, font):
    text = text.upper()

    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    if len(text) > 1:
        angle_step = arc_span / (len(text) - 1)
    else:
        angle_step = 0

    start = start_angle - arc_span / 2

    for i, char in enumerate(text):
        angle = start + i * angle_step
        rad = math.radians(angle)

        x = center[0] + radius * math.cos(rad)
        y = center[1] + radius * math.sin(rad)

        char_img = Image.new("RGBA", (200, 200), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)

        # baseline aligned drawing
        char_draw.text((100,100), char, font=font, fill="black", anchor="mm")

        rotated = char_img.rotate(angle + 90, resample=Image.BICUBIC)

        # 🔥 BASELINE SHIFT (FINAL KEY)
        draw.bitmap((x-100, y-100 - text_height * 0.35), rotated)

# Center text

def draw_center(draw, center, text, font):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center[0]-w/2, center[1]-h/2), text, fill="black", font=font)

# Generator

def generate(df, templates):
    results = []

    for _, row in df.iterrows():
        name = str(row["name"])
        city = str(row["city"])

        for t in templates:
            img = Image.open(t).convert("RGBA")
            draw = ImageDraw.Draw(img)

            center = (img.width//2, img.height//2)

            outer = img.width * 0.44
            inner = img.width * 0.30

            font_outer = get_font(font_size)
            ascent, descent = font_outer.getmetrics()
            text_height = ascent + descent

            base_radius = inner + (outer-inner) * radius_adjust

            # 🔥 FINAL PERFECT RADIUS
            radius = int(base_radius - text_height * 0.8)

            draw_circular_text(draw, center, radius, name, font_outer)

            font_center = get_font(int(font_size*1.5))
            draw_center(draw, center, city.upper(), font_center)

            results.append((img, f"{name}_{city}_{t.name}"))

    return results

# MAIN
if uploaded_file and templates:
    df = pd.read_excel(uploaded_file)
    df.columns = [c.lower() for c in df.columns]

    st.subheader("👀 Preview")
    previews = generate(df.head(2), templates)

    for img, name in previews:
        st.image(img, caption=name)

    if st.button("🚀 Generate"):
        os.makedirs("out", exist_ok=True)
        files = []

        outputs = generate(df, templates)

        for img, name in outputs:
            path = f"out/{name}.png"
            img.save(path)
            files.append(path)

        zip_path = "stamps.zip"
        with zipfile.ZipFile(zip_path, 'w') as z:
            for f in files:
                z.write(f, os.path.basename(f))

        with open(zip_path, "rb") as f:
            st.download_button("⬇️ Download", f, file_name="stamps.zip")

        st.success("✅ Pixel-perfect output generated")

# requirements
# streamlit
# pandas
# pillow
# openpyxl
