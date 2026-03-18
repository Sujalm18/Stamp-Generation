import streamlit as st
import pandas as pd
import os
import zipfile
import base64

st.set_page_config(page_title="Stamp Generator", layout="centered")
st.title("🖋️ Stamp Generator (Final)")

# =========================
# CONTROLS (TUNED)
# =========================
outer_size = st.slider("Outer Text Size", 20, 80, 42)
center_size = st.slider("Center Text Size", 30, 120, 80)
letter_spacing = st.slider("Letter Spacing", 0, 5, 1)

uploaded_excel = st.file_uploader("Upload Excel (Name, City)", type=["xlsx"])

# =========================
# SVG ENGINE (PIXEL PERFECT)
# =========================
def create_svg(name, city):
    name = name.upper()
    city = city.upper()

    # Proper circular text with separators
    text = f"{name} • {name}"

    outer_r = 200
    inner_r = 180

    # 🔥 FINAL TUNED VALUE (VISUAL CENTER)
    text_r = 186

    svg = f"""
    <svg width="500" height="500" viewBox="0 0 500 500"
         xmlns="http://www.w3.org/2000/svg">

        <rect width="100%" height="100%" fill="#0b1220"/>

        <!-- Rings -->
        <circle cx="250" cy="250" r="{outer_r}" stroke="#2d5bd1" stroke-width="6" fill="none"/>
        <circle cx="250" cy="250" r="{inner_r}" stroke="#2d5bd1" stroke-width="3" fill="none"/>
        <circle cx="250" cy="250" r="120" stroke="#2d5bd1" stroke-width="5" fill="none"/>

        <!-- TEXT PATHS -->
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
              fill="white"
              font-family="Helvetica, Arial"
              letter-spacing="{letter_spacing}">
            <textPath href="#topArc" startOffset="50%" text-anchor="middle">
                {text}
            </textPath>
        </text>

        <!-- BOTTOM TEXT -->
        <text font-size="{outer_size}"
              fill="white"
              font-family="Helvetica, Arial"
              letter-spacing="{letter_spacing}">
            <textPath href="#bottomArc" startOffset="50%" text-anchor="middle">
                {text[::-1]}
            </textPath>
        </text>

        <!-- CENTER TEXT -->
        <text x="250" y="270"
              text-anchor="middle"
              font-size="{center_size}"
              fill="white"
              font-family="Helvetica, Arial"
              font-weight="bold">
            {city}
        </text>

        <!-- STAR -->
        <text x="250" y="392"
              text-anchor="middle"
              font-size="38"
              fill="#2d5bd1">★</text>

    </svg>
    """
    return svg

# =========================
# RENDER SVG (FIXED)
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

        # =========================
        # GENERATE
        # =========================
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

            st.success("✅ Pixel-perfect stamps generated")
