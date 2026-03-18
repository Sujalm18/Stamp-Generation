# 🚀 STREAMLIT STAMP GENERATOR (IMPROVED WITH PREVIEW + BETTER OUTPUT)

import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")

st.title("🖋️ Stamp Generator (Pro Version)")
st.write("Upload Excel + Templates → Preview → Download")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
uploaded_templates = st.file_uploader("Upload Stamp Templates (PNG)", type=["png"], accept_multiple_files=True)

# Load better font (fallback safe)
def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# Better circular text (arc style)
def draw_arc_text(draw, center, radius, text, font, start_angle=0):
    text = text.upper()
    total_angle = 180  # spread text across half circle
    char_angle = total_angle / max(len(text),1)

    angle = start_angle - total_angle / 2

    for char in text:
        rad = math.radians(angle)
        x = center[0] + radius * math.cos(rad)
        y = center[1] + radius * math.sin(rad)

        # rotate character
        temp_img = Image.new("RGBA", (200, 200), (0,0,0,0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((100,100), char, font=font, fill="black", anchor="mm")

        rotated = temp_img.rotate(angle+90, resample=Image.BICUBIC, center=(100,100))
        draw.bitmap((x-100, y-100), rotated)

        angle += char_angle

# Generate stamps
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

            # dynamic sizing
            font_big = get_font(int(img.width * 0.06))
            font_small = get_font(int(img.width * 0.045))

            draw_arc_text(draw, center, int(img.width*0.38), name, font_big, start_angle=0)
            draw_arc_text(draw, center, int(img.width*0.25), city, font_small, start_angle=180)

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

            previews = generate_preview(df.head(3), uploaded_templates)  # preview first 3 rows

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

                st.success("✅ Done!")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Now with preview + proper circular text rendering")

# requirements.txt
# streamlit
# pandas
# pillow
# openpyxl
