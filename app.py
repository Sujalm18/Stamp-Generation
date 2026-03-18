import streamlit as st
import pandas as pd
import base64
import zipfile
import os

st.set_page_config(page_title="Stamp Generator PRO", layout="centered")
st.title("🖋️ Smart Stamp Generator")

# =========================
# 🧠 AUTO TEMPLATE SELECTOR
# =========================
def choose_template(name):
    name = name.strip()

    if name.replace(" ", "").isdigit():
        return "Number"

    length = len(name)

    if length < 18:
        return "Simple"
    elif length < 30:
        return "Company"
    else:
        return "Compact"


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
        return 28, 0.8, 185


# =========================
# 🎨 SVG GENERATOR
# =========================
def create_svg(name, city):
    name = name.upper()
    city = city.upper()

    template = choose_template(name)
    font_size, spacing, radius = compute_text_settings(name)

    # Avoid repetition for long text
    if len(name) > 30:
        circular_text = name
    else:
        circular_text = f"{name} • {name}"

    # Center text logic
    if template == "Company":
        center_text = "AUTHORISED SIGNATORY"
    elif template == "Simple":
        center_text = city
    elif template == "Compact":
        center_text = city
        font_size -= 4
        spacing -= 0.2
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

        <!-- Arc Paths -->
        <defs>
            <path id="topArc"
                  d="M {250 - radius} 250
                     A {radius} {radius} 0 0 1 {250 + radius} 250"/>
            <path id="bottomArc"
                  d="M {250 + radius} 250
                     A {radius} {radius} 0 0 1 {250 - radius} 250"/>
        </defs>

        <!-- TOP TEXT -->
        <text font-size="{font_size}"
              fill="#2d5bd1"
              font-family="Arial"
              letter-spacing="{spacing}">
            <textPath href="#topArc"
                      startOffset="50%"
                      text-anchor="middle"
                      dy="8">
                {circular_text}
            </textPath>
        </text>

        <!-- BOTTOM TEXT -->
        <text font-size="{font_size}"
              fill="#2d5bd1"
              font-family="Arial"
              letter-spacing="{spacing}">
            <textPath href="#bottomArc"
                      startOffset="50%"
                      text-anchor="middle"
                      dy="-8">
                {circular_text[::-1]}
            </textPath>
        </text>

        <!-- CENTER TEXT -->
        <text x="250" y="270"
              text-anchor="middle"
              font-size="70"
              fill="#2d5bd1"
              font-family="Arial"
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
# 🖼️ SAFE PREVIEW RENDER
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

        st.caption(f"Auto Template: {choose_template(df.iloc[0]['name'])}")

        # =========================
        # 🚀 BULK GENERATION
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

            st.success("✅ All stamps generated successfully!")
