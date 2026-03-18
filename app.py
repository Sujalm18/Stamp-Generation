import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import os
import zipfile

st.set_page_config(page_title="Stamp Generator", layout="centered")
st.title("🖋️ Final Professional Stamp Generator")

# =========================
# 🎛️ CONTROLS
# =========================
font_size = st.slider("Font Size", 20, 80, 40)

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
# 🔥 PERFECT CIRCULAR TEXT (WIDTH-BASED)
# =========================
def draw_circular_text(draw, center, radius, text, font):
    text = text.upper()

    # Measure each character width
    char_widths = [draw.textlength(c, font=font) for c in text]
    total_width = sum(char_widths)

    circumference = 2 * math.pi * radius
    angle_per_pixel = 360 / circumference

    total_angle = total_width * angle_per_pixel
    start_angle = -90 - total_angle / 2

    current_angle = start_angle

    for i, char in enumerate(text):
        char_width = char_widths[i]
        char_angle = char_width * angle_per_pixel

        angle = current_angle + char_angle / 2
        rad = math.radians(angle)

        x = center[0] + radius * math.cos(rad)
        y = center[1] + radius * math.sin(rad)

        CHAR_BOX = int(font.size * 1.3)

        char_img = Image.new("RGBA", (CHAR_BOX, CHAR_BOX), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)

        char_draw.text(
            (CHAR_BOX // 2, CHAR_BOX // 2),
            char,
            font=font,
            fill="black",
            anchor="mm"
        )

        # ✅ OUTWARD + TANGENTIAL
        rotated = char_img.rotate(angle - 90, resample=Image.BICUBIC)

        draw.bitmap(
            (x - CHAR_BOX // 2, y - CHAR_BOX // 2),
            rotated
        )

        current_angle += char_angle

# =========================
# 📍 CENTER TEXT
# =========================
def draw_center(draw, center, text, font):
    lines = text.split("\n")
    y_offset = 0

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(
            (center[0] - w / 2, center[1] + y_offset - h / 2),
            line,
            fill="black",
            font=font
        )

        y_offset += h

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

            font_outer = get_font(font_size)

            # 🔥 PERFECT BAND CENTER
            radius = int(inner + (outer - inner) * 0.5)

            draw_circular_text(draw, center, radius, name, font_outer)

            # Center text (clean)
            font_center = get_font(int(font_size * 1.3))
            draw_center(draw, center, city.upper(), font_center)

            results.append((img, f"{name}_{city}_{t.name}"))

    return results

# =========================
# 🧠 MAIN FLOW
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

        st.success("✅ Perfect Stamp Generated")
