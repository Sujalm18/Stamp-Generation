import streamlit as st
import pandas as pd
import base64
import zipfile
import os

st.set_page_config(page_title="Stamp Generator PRO", layout="centered")
st.title("🖋️ Multi-Template Stamp Generator")

# =========================
# TEMPLATE SELECTOR
# =========================
template = st.selectbox(
    "Choose Template",
    [
        "Company Seal",
        "Bank Stamp",
        "Simple Seal",
        "Number Seal"
    ]
)

outer_size = st.slider("Outer Text Size", 20, 80, 42)
center_size = st.slider("Center Text Size", 20, 120, 60)

uploaded_excel = st.file_uploader("Upload Excel", type=["xlsx"])

# =========================
# SVG RENDER
# =========================
def render_svg(svg):
    b64 = base64.b64encode(svg.encode()).decode()
    st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" width="420"/>', unsafe_allow_html=True)

# =========================
# TEMPLATE ENGINE
# =========================
def create_svg(name, city, extra=""):
    name = name.upper()
    city = city.upper()

    text_r = 186

    if template == "Company Seal":
        center_text = "AUTHORISED SIGNATORY"
        bottom = text = f"{name} • {name}"

    elif template == "Bank Stamp":
        center_text = f"Branch {extra if extra else '0004'}"
        bottom = f"{city} BRANCH"
        text = name

    elif template == "Simple Seal":
        center_text = city
        bottom = text = f"{name} • {name}"

    elif template == "Number Seal":
        center_text = extra if extra else "0123456"
        bottom = text = name

    svg = f"""
    <svg width="500" height="500" viewBox="0 0 500 500"
         xmlns="http://www.w3.org/2000/svg">

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

        <!-- TOP -->
        <text font-size="{outer_size}" fill="#2d5bd1"
              font-family="Arial" letter-spacing="1">
            <textPath href="#topArc" startOffset="50%" text-anchor="middle">
                {text}
            </textPath>
        </text>

        <!-- BOTTOM -->
        <text font-size="{outer_size}" fill="#2d5bd1"
              font-family="Arial" letter-spacing="1">
            <textPath href="#bottomArc" startOffset="50%" text-anchor="middle">
                {bottom[::-1]}
            </textPath>
        </text>

        <!-- CENTER -->
        <text x="250" y="265"
              text-anchor="middle"
              font-size="{center_size}"
              fill="#2d5bd1"
              font-family="Arial"
              font-weight="bold">
            {center_text}
        </text>

        <!-- STAR -->
        <text x="250" y="390"
              text-anchor="middle"
              font-size="32"
              fill="#2d5bd1">★</text>

    </svg>
    """

    return svg


# =========================
# MAIN
# =========================
if uploaded_excel:
    df = pd.read_excel(uploaded_excel)
    df.columns = [c.lower() for c in df.columns]

    st.subheader("👀 Preview")

    preview_svg = create_svg(
        df.iloc[0]["name"],
        df.iloc[0]["city"]
    )

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

        st.success("✅ All templates generated")
