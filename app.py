import streamlit as st
import pandas as pd
import base64
import zipfile
import os

st.set_page_config(page_title="Stamp Generator PRO", layout="centered")
st.title("🖋️ Smart Stamp Generator")

# =========================
# 🧠 SCALING ENGINE
# =========================
def compute_text_settings(name):
    length = len(name)

    if length < 18:
        return 36, 2
    elif length < 26:
        return 32, 1.5
    elif length < 34:
        return 28, 1.2
    else:
        return 24, 1.0


# =========================
# 🎨 SVG GENERATOR
# =========================
def create_svg(name, city):
    name = name.upper().strip()
    city = city.upper().strip()

    TEXT_RADIUS = 190  # PERFECT center between 200 & 180

    font_size, spacing = compute_text_settings(name)

    circular_text = f"{name} • "

    svg = f"""
    <svg width="500" height="500" viewBox="0 0 500 500"
         xmlns="http://www.w3.org/2000/svg">

        <!-- Background -->
        <rect width="100%" height="100%" fill="white"/>

        <!-- Rings -->
        <circle cx="250" cy="250" r="220"
                stroke="#2d5bd1" stroke-width="5" fill="none"/>
        <circle cx="250" cy="250" r="180"
                stroke="#2d5bd1" stroke-width="2" fill="none"/>
        <circle cx="250" cy="250" r="120"
                stroke="#2d5bd1" stroke-width="3" fill="none"/>

        <!-- Circular Path -->
        <defs>
            <path id="circlePath"
                  d="
                    M 250 250
                    m -{TEXT_RADIUS}, 0
                    a {TEXT_RADIUS},{TEXT_RADIUS} 0 1,1 {TEXT_RADIUS*2},0
                    a {TEXT_RADIUS},{TEXT_RADIUS} 0 1,1 -{TEXT_RADIUS*2},0
                  "/>
        </defs>

        <!-- Circular Text -->
        <text font-size="{font_size}"
              fill="#2d5bd1"
              font-family="Arial Black, Arial"
              letter-spacing="{spacing}">
            <textPath href="#circlePath"
                      startOffset="50%"
                      text-anchor="middle">
                {circular_text * 6}
            </textPath>
        </text>

        <!-- Center Text -->
        <text x="250" y="255"
              text-anchor="middle"
              font-size="42"
              fill="#2d5bd1"
              font-family="Arial Black, Arial">
            {city}
        </text>

        <!-- Star -->
        <text x="250" y="385"
              text-anchor="middle"
              font-size="28"
              fill="#2d5bd1">★</text>

    </svg>
    """

    return svg


# =========================
# 🖼️ PREVIEW RENDER
# =========================
def render_svg(svg):
    b64 = base64.b64encode(svg.encode()).decode()
    html = f'<img src="data:image/svg+xml;base64,{b64}" width="420"/>'
    st.markdown(html, unsafe_allow_html=True)


# =========================
# 📂 FILE INPUT
# =========================
uploaded_excel = st.file_uploader("Upload Excel (Name, City)", type=["xlsx"])

if uploaded_excel:
    df = pd.read_excel(uploaded_excel)
    df.columns = [c.lower() for c in df.columns]

    if "name" not in df.columns or "city" not in df.columns:
        st.error("Excel must contain columns: Name, City")
    else:
        st.subheader("👀 Preview")

        preview_svg = create_svg(df.iloc[0]["name"], df.iloc[0]["city"])
        render_svg(preview_svg)

        # =========================
        # 🚀 GENERATE ALL
        # =========================
        if st.button("Generate Stamps"):
            os.makedirs("out", exist_ok=True)
            zip_path = "stamps.zip"

            with zipfile.ZipFile(zip_path, "w") as z:
                for _, row in df.iterrows():
                    svg = create_svg(row["name"], row["city"])

                    filename = f"{row['name']}_{row['city']}.svg"
                    filepath = f"out/{filename}"

                    with open(filepath, "w") as f:
                        f.write(svg)

                    z.write(filepath, filename)

            with open(zip_path, "rb") as f:
                st.download_button("⬇️ Download ZIP", f, file_name="stamps.zip")

            st.success("✅ Stamps generated successfully!")
