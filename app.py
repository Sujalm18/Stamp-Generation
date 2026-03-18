import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import os
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")
st.title("🖋️ Professional Stamp Generator")

# =========================
# 🎛️ CONTROLS
# =========================
font_size = st.slider("Font Size", 30, 120, 60)
arc_strength = st.slider("Arc Strength", 0.8, 2.0, 1.2)

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
# 🔍 DETECT RING
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
# 🔥 REAL CURVED TEXT ENGINE
# =========================
def draw_curved_text(img, center, radius, text, font):
    text = text.upper()

    # Step 1: render straight text
    dummy = Image.new("RGBA", (3000, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(dummy)

    bbox = d.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    txt_img = Image.new("RGBA", (text_w, text_h), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(txt_img)
    d2.text((0, 0), text, font=font, fill="black")

    result = img.copy()

    # Step 2: map text onto arc
    for x in range(text_w):
        for y in range(text_h):
            px = txt_img.getpixel((x, y))
            if px[3] == 0:
                continue

            # angle mapping (centered)
            angle = (x / text_w - 0.5) * math.pi * arc_strength

            r = radius - y

            new_x = int(center[0] + r * math.cos(angle - math.pi/2))
            new_y = int(center[1] + r * math.sin(angle - math.pi/2))

            if 0 <= new_x < img.width and 0 <= new_y < img.height:
                result.putpixel((new_x, new_y), px)

    return result

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
# 🚀 GENERATE
# =========================
def generate(df, templates):
    results = []

    for _, row in df.iterrows():
        name = str(row["name"])
        city = str(row["city"])

        for t in templates:
            img = Image.open(t).convert("RGBA")

            center = (img.width // 2, img.height // 2)

            inner, outer = detect_ring_radii(img)

            if inner is None:
                inner = img.width * 0.30
                outer = img.width * 0.45

            font_outer = get_font(font_size)

            # 🔥 PERFECT POSITION INSIDE BAND
            radius = int(inner + (outer - inner) * 0.65)

            img = draw_curved_text(img, center, radius, name, font_outer)

            draw = ImageDraw.Draw(img)

            font_center = get_font(int(font_size * 0.8))
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

        st.success("✅ Final Stamp Generated")
