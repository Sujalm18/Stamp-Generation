import streamlit as st
import pandas as pd
import base64
import zipfile
import os

st.set_page_config(page_title="Stamp Generator PRO", layout="centered")
st.title("🖋️ Stamp Generator (Pro Max)")

# =========================
# TEMPLATE SELECTOR
# =========================
template = st.selectbox(
    "Template",
    ["Company Seal", "Simple Seal", "Number Seal"]
)

uploaded_excel = st.file_uploader("Upload Excel (Name, City)", type=["xlsx"])

# =========================
# 🔥 PERFECT SCALING ENGINE
# =========================
def compute_text_settings(name):
    length = len(name)

    if length <= 18:
        return 44, 1.5, 182
    elif length <= 26:
        return 38, 1.2, 183
    elif length <= 34:
        return 34, 1.0, 184
    else:
        return 30, 0.8, 185


# =========================
# SVG ENGINE
# =========================
def create_svg(name, city):
    name = name.upper()
    city = city.upper()

    outer_size, spacing, text_r = compute_text_settings(name)

    text = f"{name} • {name}"

    if template == "Company Seal":
        center_text = "AUTHORISED SIGNATORY"
    elif template == "Simple Seal":
        center_text = city
    else:
        center_text = "0123456"

    svg = f"""
    <svg width="500" height="500" viewBox="0 0 500 500"
         xmlns="http://www.w3.org/2000/svg">

        <!-- Background -->
        <rect width="100%" height="100%" fill="white"/>

        <!-- Rings -->
        <circle cx="250" cy="250" r="200" stroke="#2d5bd1" stroke-width="5" fill="none"/>
        <circle cx="250" cy="250" r="180" stroke="#2d5bd1" stroke-width="2" fill="none"/>
        <circle cx="250" cy="250" r="120" stroke="#2d5bd1" stroke-width="3" fill="none"/>

        <!-- Paths -->
        <defs>
            <path id="topArc"
                  d="M {250 - text_r} 250
                     A {text_r} {text_r} 0 0 1 {250 + text_r} 250"/>
            <path id="bottomArc"
                  d="M {250 + text_r} 250
                     A {text_r} {text_r} 0 0 1 {250 - text_r} 250"/>
        </defs>

        <!-- TOP TEXT -->
        <text font-size="{outer_size}"
              fill="#2d5bd1"
              font-family="Helvetica, Arial"
              letter-spacing="{spacing}">
            <textPath href="#topArc"
                      startOffset="50%"
                      text-anchor="middle"
                      dy="8">
                {text}
            </textPath>
        </text>

        <!-- BOTTOM TEXT -->
        <text font-size="{outer_size}"
              fill="#2d5bd1"
              font-family="Helvetica, Arial"
              letter-spacing="{spacing}">
            <textPath href="#bottomArc"
                      startOffset="50%"
                      text-anchor="middle"
                      dy="-8">
                {text[::-1]}
            </textPath>
        </text>

        <!-- CENTER TEXT -->
        <text x="250" y="270"
              text-anchor="middle"
              font-size="70"
              fill="#2d5bd1"
              font-family="Helvetica, Arial"
              font-weight="bold">
            {center_text}
        </text>

        <!-- STAR -->
        <text x="250" y="390"
              text-anchor="middle"
              font-size="36"
              fill="#2d5bd1">★</text>

    </svg>
    """

    return svg


# =========================
# SVG RENDER (FIXED)
# =========================
def render_svg(svg):
    b64 = base64.b64encode(svg.encode()).decode()
    html = f'<img src="data:image/svg+xml;base64,{b64}" width="420"/>'
    st.markdown(html, unsafe_allow_html=True)


# =========================
# MAIN
# =========================
if uploaded_excel:
    df = pd.read_excel(uploaded_excel)
    df.columns = [c.lower() for c in df.columns]

    if "name" not in df.columns or "city" not in df.columns:
        st.error("Excel must contain 'Name' and 'City'")
    else:
        st.subheader("👀 Preview")

        preview_svg = create_svg(df.iloc[0]["name"], df.iloc[0]["city"])
        render_svg(preview_svg)

        if st.button("🚀 Generate All"):
            os.makedirs("out", exist_ok=True)
            zip_path = "stamps.zip"

            with zipfile.ZipFile(zip_path, "w") as z:
                for _, row in df.iterrows():
                    svg = create_svg(row["name"], row["city"])

                    filename = f"{row['name']}_{row['city']}.svg"
                    path = f"out/{filename}"

                    with open(path, "w") as f:
                        f.write(svg)

                    z.write(path, filename)

            with open(zip_path, "rb") as f:
                st.download_button("⬇️ Download ZIP", f, file_name="stamps.zip")

            st.success("✅ Perfect stamps generated")
