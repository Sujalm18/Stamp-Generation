import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import os
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")
st.title("🖋️ Advanced Stamp Generator")

# =========================
# 🎛️ CONTROLS
# =========================
font_size = st.slider("Font Size", 20, 80, 40)
arc_span = st.slider("Arc Span", 80, 180, 120)
start_angle = st.slider("Start Angle", -180, 180, -90)

letter_spacing = st.slider("Letter Spacing", 0.5, 3.0, 1.2)
radius_offset = st.slider("Radius Adjust", -50, 50, 0)
text_offset = st.slider("Text Vertical Offset", -50, 50, 0)
font_scale = st.slider("Font Scale", 0.5, 2.0, 1.0)

uploaded_excel = st.file_uploader("Upload Excel (Name, City)", type=["xlsx"])
uploaded_templates = st.file_uploader(
    "Upload Templates (PNG)", type=["png"], accept_multiple_files=True
)

# =========================
# 🔤 FONT
# =========================
def get_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# =========================
# 🔍 AUTO DETECT RING
# =========================
def detect_ring_radii(img):
    img_np = np.array(img)

    blue_mask = (
        (img_np[:, :, 2] > 150) &
        (img_np[:, :, 1] < 120) &
        (img_np[:, :, 0] < 120)
    )

    h, w = blue_mask.shape
    cx, cy = w // 2, h // 2

    radii = []

    for x in range(cx, w):
        if blue_mask[cy, x]:
            radii.append(x - cx)

    if len(radii) < 10:
        return None, None

    return min(radii), max(radii)

# =========================
# 🔥 DRAW TEXT ON ARC
# =========================
def draw_circular_text(draw, center, radius, text, font):
    text = text.upper()

    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    if len(text) > 1:
        step = (arc_span / (len(text) - 1)) * letter_spacing
    else:
        step = 0

    start = start_angle - arc_span / 2

    for i, char in enumerate(text):
        angle = start + i * step
        rad = math.radians(angle)

        x = center[0] + radius * math.cos(rad)
        y = center[1] + radius * math.sin(rad)

        # 🔥 FIXED CHAR BOX
        CHAR_BOX = int(font.size * 1.2)

        char_img = Image.new("RGBA", (CHAR_BOX, CHAR_BOX), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)

        char_draw.text(
            (CHAR_BOX // 2, CHAR_BOX // 2),
            char,
            font=font,
            fill="black",
            anchor="mm"
        )

        # ✅ OUTWARD FACING TEXT
        rotated = char_img.rotate(angle - 90, resample=Image.BICUBIC)

        draw.bitmap(
            (
                x - CHAR_BOX // 2,
                y - CHAR_BOX // 2 - text_height * 0.25 + text_offset
            ),
            rotated
        )

# =========================
# 📍 CENTER TEXT
# =========================
def draw_center(draw, center, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    draw.text(
        (center[0] - w / 2, center[1] - h / 2),
        text,
        fill="black",
        font=font
    )

# =========================
# 🚀 GENERATE STAMPS
# =========================
def generate(df, templates):
    results = []

    for _, row in df.iterrows():
        name = str(row["name"])
        city = str(row["city"])

        for t in templates:
            img = Image.open(t).convert("RGBA")
            draw = ImageDraw.Draw(img)

            center = (img.width // 2, img.height // 2)

            inner, outer = detect_ring_radii(img)

            if inner is None:
                inner = img.width * 0.30
                outer = img.width * 0.44

            font_outer = get_font(int(font_size * font_scale))

            ascent, descent = font_outer.getmetrics()
            text_height = ascent + descent

            base_radius = (inner + outer) / 2

            # 🔥 FINAL RADIUS FIX
            radius = int(base_radius - text_height * 0.4 + radius_offset)

            draw_circular_text(draw, center, radius, name, font_outer)

            font_center = get_font(int(font_size * 1.5))
            draw_center(draw, center, city.upper(), font_center)

            results.append((img, f"{name}_{city}_{t.name}"))

    return results

# =========================
# 🧠 MAIN
# =========================
if uploaded_excel and uploaded_templates:
    df = pd.read_excel(uploaded_excel)
    df.columns = [c.lower() for c in df.columns]

    st.subheader("👀 Preview")
    previews = generate(df.head(2), uploaded_templates)

    for img, name in previews:
        st.image(img, caption=name)

    if st.button("🚀 Generate"):
        os.makedirs("out", exist_ok=True)
        files = []

        outputs = generate(df, uploaded_templates)

        for img, name in outputs:
            path = f"out/{name}.png"
            img.save(path)
            files.append(path)

        zip_path = "stamps.zip"
        with zipfile.ZipFile(zip_path, "w") as z:
            for f in files:
                z.write(f, os.path.basename(f))

        with open(zip_path, "rb") as f:
            st.download_button("⬇️ Download ZIP", f, file_name="stamps.zip")

        st.success("✅ Perfect Output Generated")
