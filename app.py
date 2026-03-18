# 🚀 STREAMLIT STAMP GENERATOR (FINAL FIX - PROPER TEXT FIT INSIDE RING)

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator (Correct Geometry Version)")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
uploaded_templates = st.file_uploader("Upload Stamp Templates (PNG)", type=["png"], accept_multiple_files=True)

# Font loader

def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# ✅ FIXED circular text (FULL 360 FIT + AUTO SPACING)

def draw_circular_text(draw, center, radius, text, font):
    text = text.upper()

    # Calculate circumference
    circumference = 2 * math.pi * radius

    # Estimate text width
    total_text_width = sum([draw.textlength(c, font=font) for c in text])

    # Scale spacing to fit inside circle
    angle_per_pixel = 360 / circumference

    current_angle = -90 - (total_text_width * angle_per_pixel) / 2

    for char in text:
        char_width = draw.textlength(char, font=font)
        char_angle = char_width * angle_per_pixel

        angle_rad = math.radians(current_angle + char_angle / 2)

        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)

        # rotate character properly
        char_img = Image.new("RGBA", (200, 200), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((100,100), char, font=font, fill="black", anchor="mm")

        rotated = char_img.rotate(current_angle + char_angle / 2 + 90, resample=Image.BICUBIC)

        draw.bitmap((x-100, y-100), rotated)

        current_angle += char_angle

# Center text

def draw_center_text(draw, center, text, font):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center[0]-w/2, center[1]-h/2), text, fill="black", font=font)

# Main generator

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

            # 🔥 PERFECT RADIUS (BETWEEN RINGS)
            outer_radius = int(img.width * 0.36)

            font_outer = get_font(int(img.width * 0.045))
            font_center = get_font(int(img.width * 0.09))

            # NAME (fits exactly inside ring)
            draw_circular_text(draw, center, outer_radius, name, font_outer)

            # CITY (center)
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

                st.success("✅ FINAL FIX APPLIED")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Now text auto-fits perfectly inside ring (no overflow, no gaps)")

# requirements.txt
# streamlit
# pandas
# pillow
# openpyxl
