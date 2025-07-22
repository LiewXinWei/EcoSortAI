import streamlit as st
import folium
from streamlit_folium import folium_static

# Custom icon path
BIN_ICON_PATH = "bin.png"

# List of SG bin locations
locations = [
    (1.3521, 103.8198, "Central Singapore"),
    (1.290270, 103.851959, "Marina Bay Sands"),
    (1.2816, 103.8636, "Gardens by the Bay"),
    (1.4360, 103.7865, "Woodlands"),
    (1.3048, 103.8318, "Orchard Road"),
    (1.3331, 103.7430, "Jurong East"),
    (1.3736, 103.9492, "Pasir Ris"),
    (1.3245, 103.9301, "Bedok"),
    (1.3496, 103.9568, "Tampines"),
    (1.3784, 103.7649, "Bukit Panjang"),
    (1.3145, 103.8650, "Geylang"),
    (1.2842, 103.8430, "Chinatown"),
    (1.3065, 103.8492, "Little India"),
    (1.2992, 103.8554, "Bugis"),
    (1.3500, 103.8480, "Bishan"),
    (1.3496, 103.8739, "Serangoon"),
    (1.3611, 103.8864, "Hougang"),
    (1.3691, 103.8480, "Ang Mo Kio"),
    (1.3340, 103.8500, "Toa Payoh"),
    (1.3122, 103.8660, "Kallang"),
    (1.2941, 103.7858, "Queenstown"),
    (1.3294, 103.8021, "Bukit Timah"),
    (1.3151, 103.7656, "Clementi"),
    (1.3496, 103.7490, "Bukit Batok"),
    (1.4294, 103.8355, "Yishun"),
    (1.4491, 103.8201, "Sembawang"),
    (1.4043, 103.9021, "Punggol"),
    (1.3911, 103.8950, "Sengkang"),
    (1.3894, 103.9872, "Changi"),
    (1.4051, 103.8690, "Seletar"),
]

# Streamlit UI
st.set_page_config(page_title="SG Recycling Map", layout="wide")
st.title("♻️ Find the Nearest Recycling Bin in Singapore")

# Your requested input lines
user_input = st.text_input("Enter your current location :", "your location")
user_input = st.text_input("Enter your current location :", "choose destination")

# Dummy/default map center
default_location = [1.3521, 103.8198]
m = folium.Map(location=default_location, zoom_start=12)

# Add all bins
for lat, lon, name in locations:
    icon = folium.CustomIcon(BIN_ICON_PATH, icon_size=(30, 30))
    folium.Marker(
        location=[lat, lon],
        popup=f"Recycling Bin at {name}",
        tooltip=name,
        icon=icon
    ).add_to(m)

# Display the map
folium_static(m)

# Static "Nearest Recycling Centers" section
st.markdown("### 📌 Nearest Recycling Centers:")
st.markdown("""
- **EcoSort Center** – *250 m* (nearest)  
- **EcoSort Center** – *300 m*
- **EcoSort Center** – *670 m*
""")

st.markdown("---")

