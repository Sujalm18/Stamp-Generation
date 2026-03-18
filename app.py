# 🚀 STREAMLIT STAMP GENERATOR (FIXED PROFESSIONAL VERSION)

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator (Accurate Version)")
st.write("Now text fits perfectly inside the stamp")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
uploaded_templates = st.file_uploader("Upload Stamp Templates (PNG)", type=["png"], accept_multiple_files=True)

# Font loader
def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# ✅ IMPROVED circular text (PROPER spacing + alignment)
def draw_circular_text(draw, center, radius, text, font, start_angle=0, spacing=12):
    text = text.upper()

    # total arc based on spacing
    total_angle = spacing * len(text)
    angle = start_angle - total_angle / 2

    for char in text:
        angle_rad = math.radians(angle)

        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)

        # create rotated character
        char_img = Image.new("RGBA", (150, 150), (0,0,0,0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((75,75), char, font=font, fill="black", anchor="mm")

        rotated = char_img.rotate(angle + 90, resample=Image.BICUBIC)

        draw.bitmap((x-75, y-75), rotated)

        angle += spacing

# ✅ CENTER TEXT FUNCTION (for city)
def draw_center_text(draw, center, text, font):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center[0]-w/2, center[1]-h/2), text, fill="black", font=font)

# Generate previews

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

            # 🔥 KEY FIXES (based on your UI values)
            outer_radius = int(img.width * 0.42)   # inside outer ring
            inner_radius = int(img.width * 0.30)   # for inner text if needed

            font_outer = get_font(int(img.width * 0.045))
            font_center = get_font(int(img.width * 0.08))

            # NAME → around circle (top half)
            draw_circular_text(draw, center, outer_radius, name, font_outer, start_angle=270, spacing=10)

            # CITY → center
            draw_center_text(draw, center, city.upper(), font_center)

            previews.append((img, f"{name}_{city}_{template_file.name}"))

    return previews

if uploaded_file and uploaded_templates:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [col.lower() for col in df.columns]

        if "name" not in df.columns or "city" not in df.columns:
            st.error("Excel must contain 'Name' and 'City'")
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

                st.success("✅ Perfect stamps generated!")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Now properly aligned: Name on ring, City at center")

# requirements.txt
# streamlit
# pandas
# pillow
# openpyxl
