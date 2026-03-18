import streamlit as st
import pandas as pd
import os
import zipfile
import cairosvg

st.set_page_config(page_title="Stamp Generator PRO", layout="centered")

st.title("🖋️ Stamp Generator (Production Ready)")

# =========================
# 🎛️ CONTROLS
# =========================
outer_text_size = st.slider("Outer Text Size", 20, 80, 40)
center_text_size = st.slider("Center Text Size", 30, 120, 70)
letter_spacing = st.slider("Letter Spacing", 0, 10, 2)

uploaded_excel = st.file_uploader("Upload Excel (Name, City)", type=["xlsx"])


# =========================
# 🔥 SVG ENGINE (PERFECT)
# =========================
def create_svg(name, city):
    name = name.upper()
    city = city.upper()

    # Add separators like real stamp
    full_text = f"{name} • {name}"

    svg = f"""
    <svg width="500" height="500" viewBox="0 0 500 500"
         xmlns="http://www.w3.org/2000/svg">

        <!-- Background -->
        <rect width="100%" height="100%" fill="#0b1220"/>

        <!-- Rings -->
        <circle cx="250" cy="250" r="200" stroke="#2d5bd1" stroke-width="6" fill="none"/>
        <circle cx="250" cy="250" r="180" stroke="#2d5bd1" stroke-width="3" fill="none"/>
        <circle cx="250" cy="250" r="120" stroke="#2d5bd1" stroke-width="5" fill="none"/>

        <!-- Paths -->
        <defs>
            <!-- Top arc -->
            <path id="topArc"
                  d="M 50 250 A 200 200 0 0 1 450 250"/>

            <!-- Bottom arc (correct orientation) -->
            <path id="bottomArc"
                  d="M 450 250 A 200 200 0 0 1 50 250"/>
        </defs>

        <!-- Top Text -->
        <text font-size="{outer_text_size}"
              fill="white"
              font-family="Arial"
              letter-spacing="{letter_spacing}">
            <textPath href="#topArc"
                      startOffset="50%"
                      text-anchor="middle">
                {full_text}
            </textPath>
        </text>

        <!-- Bottom Text (flipped properly) -->
        <text font-size="{outer_text_size}"
              fill="white"
              font-family="Arial"
              letter-spacing="{letter_spacing}">
            <textPath href="#bottomArc"
                      startOffset="50%"
                      text-anchor="middle">
                {full_text[::-1]}
            </textPath>
        </text>

        <!-- Center Text -->
        <text x="250" y="265"
              text-anchor="middle"
              font-size="{center_text_size}"
              fill="white"
              font-family="Arial"
              font-weight="bold">
            {city}
        </text>

        <!-- Star -->
        <text x="250" y="395"
              text-anchor="middle"
              font-size="40"
              fill="#2d5bd1">★</text>

    </svg>
    """

    return svg


# =========================
# 🚀 MAIN LOGIC
# =========================
if uploaded_excel:
    df = pd.read_excel(uploaded_excel)
    df.columns = [c.lower() for c in df.columns]

    if "name" not in df.columns or "city" not in df.columns:
        st.error("Excel must contain 'Name' and 'City'")
    else:
        st.subheader("👀 Preview")

        svg_preview = create_svg(df.iloc[0]["name"], df.iloc[0]["city"])

        # ✅ FIXED RENDERING
        st.markdown(svg_preview, unsafe_allow_html=True)

        # =========================
        # DOWNLOAD
        # =========================
        if st.button("🚀 Generate All"):
            os.makedirs("out", exist_ok=True)

            zip_path = "stamps.zip"

            with zipfile.ZipFile(zip_path, "w") as z:
                for _, row in df.iterrows():
                    svg = create_svg(row["name"], row["city"])

                    filename = f"{row['name']}_{row['city']}"

                    svg_path = f"out/{filename}.svg"
                    png_path = f"out/{filename}.png"

                    # Save SVG
                    with open(svg_path, "w") as f:
                        f.write(svg)

                    # Convert to PNG
                    cairosvg.svg2png(bytestring=svg.encode(), write_to=png_path)

                    z.write(png_path, os.path.basename(png_path))

            with open(zip_path, "rb") as f:
                st.download_button("⬇️ Download ZIP", f, file_name="stamps.zip")

            st.success("✅ Done — Pixel Perfect Output")
