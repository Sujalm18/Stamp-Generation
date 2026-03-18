import streamlit as st
import pandas as pd
import base64
import os
import zipfile

st.set_page_config(page_title="Stamp Generator PRO", layout="centered")
st.title("🖋️ Perfect Stamp Generator (SVG Engine)")

font_size = st.slider("Outer Text Size", 20, 100, 40)
center_size = st.slider("Center Text Size", 20, 120, 70)

uploaded_excel = st.file_uploader("Upload Excel (Name, City)", type=["xlsx"])

# =========================
# 🔥 SVG STAMP GENERATOR
# =========================
def create_svg(name, city):
    name = name.upper()
    city = city.upper()

    svg = f'''
    <svg width="500" height="500" viewBox="0 0 500 500"
         xmlns="http://www.w3.org/2000/svg">

        <!-- Rings -->
        <circle cx="250" cy="250" r="200" stroke="#2d5bd1" stroke-width="6" fill="none"/>
        <circle cx="250" cy="250" r="185" stroke="#2d5bd1" stroke-width="3" fill="none"/>
        <circle cx="250" cy="250" r="120" stroke="#2d5bd1" stroke-width="5" fill="none"/>

        <!-- Paths -->
        <defs>
            <path id="topArc" d="
                M 50 250
                A 200 200 0 0 1 450 250
            "/>

            <path id="bottomArc" d="
                M 450 250
                A 200 200 0 0 1 50 250
            "/>
        </defs>

        <!-- Top Text -->
        <text font-size="{font_size}" fill="#ffffff" font-family="Roboto, Arial" letter-spacing="2">
            <textPath href="#topArc" startOffset="50%" text-anchor="middle">
                {name}
            </textPath>
        </text>

        <!-- Bottom Text -->
        <text font-size="{font_size}" fill="#ffffff" font-family="Roboto, Arial" letter-spacing="2">
            <textPath href="#bottomArc" startOffset="50%" text-anchor="middle">
                {name}
            </textPath>
        </text>

        <!-- Center -->
        <text x="250" y="270" text-anchor="middle"
              font-size="{center_size}" fill="#ffffff"
              font-family="Roboto, Arial">
            {city}
        </text>

        <!-- Star -->
        <text x="250" y="410" text-anchor="middle"
              font-size="40" fill="#2d5bd1">★</text>

    </svg>
    '''
    return svg

# =========================
# 🚀 GENERATE
# =========================
if uploaded_excel:
    df = pd.read_excel(uploaded_excel)
    df.columns = [c.lower() for c in df.columns]

    st.subheader("👀 Preview")

    preview_svg = create_svg(df.iloc[0]["name"], df.iloc[0]["city"])
    st.image(preview_svg)

    if st.button("🚀 Generate All"):
        os.makedirs("out", exist_ok=True)
        files = []

        for _, row in df.iterrows():
            svg = create_svg(row["name"], row["city"])
            filename = f'{row["name"]}_{row["city"]}.svg'
            path = f"out/{filename}"

            with open(path, "w") as f:
                f.write(svg)

            files.append(path)

        zip_path = "stamps.zip"
        with zipfile.ZipFile(zip_path, "w") as z:
            for f in files:
                z.write(f, os.path.basename(f))

        with open(zip_path, "rb") as f:
            st.download_button("⬇️ Download ZIP", f, file_name="stamps.zip")

        st.success("✅ Perfect Stamps Generated")
