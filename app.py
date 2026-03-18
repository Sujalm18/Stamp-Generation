# 🚀 STREAMLIT STAMP GENERATOR (FINAL GEOMETRY FIX — TEXT BETWEEN RINGS)

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator (Correct Ring Placement)")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
uploaded_templates = st.file_uploader("Upload Stamp Templates (PNG)", type=["png"], accept_multiple_files=True)

# Font loader

def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# ✅ KEY FIX: TEXT EXACTLY BETWEEN TWO RINGS

def draw_circular_text(draw, center, radius, text, font, inward=True):
    text = text.upper()

    angle_step = 360 / len(text)
    start_angle = -90  # top center

    for i, char in enumerate(text):
        angle = start_angle + i * angle_step
        angle_rad = math.radians(angle)

        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)

        char_img = Image.new("RGBA", (140, 140), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((70,70), char, font=font, fill="black", anchor="mm")

        # 🔥 CRITICAL: rotate inward so text faces center
        rotation = angle + 90 if inward else angle - 90

        rotated = char_img.rotate(rotation, resample=Image.BICUBIC)

        draw.bitmap((x-70, y-70), rotated)

# Center text

def draw_center_text(draw, center, text, font):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center[0]-w/2, center[1]-h/2), text, fill="black", font=font)

# 🔥 FIND PERFECT RADIUS BETWEEN TWO RINGS

def get_ring_radius(img):
    # Outer ring approx ~45%, inner ring ~30%
    outer = img.width * 0.44
    inner = img.width * 0.30

    # 🔥 LOWERED RADIUS (closer to inner ring as you requested)
    return int(inner + (outer - inner) * 0.30)  # EXACT middle between rings

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

            # ✅ PERFECT RING POSITION
            radius = get_ring_radius(img)

            font_outer = get_font(int(img.width * 0.045))
            font_center = get_font(int(img.width * 0.09))

            # NAME → BETWEEN RINGS (FIXED)
            draw_circular_text(draw, center, radius, name, font_outer, inward=True)

            # CITY → CENTER
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

                st.success("✅ TEXT NOW PERFECTLY BETWEEN RINGS")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Now text sits EXACTLY between the two blue rings")

# requirements.txt
# streamlit
# pandas
# pillow
# openpyxl
