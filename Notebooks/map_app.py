# Streamlit app displays a map of selected 5G cell coverages and user locations at ITU campus, allowing users to filter data by cell ID and neighbor range
import folium
import streamlit as st
from streamlit_folium import st_folium
import geopandas as gpd
import polars as pl

coverages = gpd.read_parquet("data/parquet/coverages/coverages.parquet")
df = pl.read_parquet("data/parquet/processed/dl.with_cluster.parquet").drop_nulls(
    ["Longitude", "Latitude"]
)  # null columns prevents marking user equipment locations on the map

gdf = gpd.GeoDataFrame(
    df.to_pandas(),
    geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
    crs="EPSG:4326",
    columns=df.columns,
)

st.set_page_config(layout="wide")
st.title("ITU Coverage Map")

col_1, col_2 = st.columns([5, 2])  # width ratio of columns on the app

m = folium.Map(location=[41.10427, 29.02554], zoom_start=15) # created starting location of the map manually

columns_to_check = [
    "NR_UE_PCI_0",
    "NR_UE_Nbr_PCI_0",
    "NR_UE_Nbr_PCI_1",
    "NR_UE_Nbr_PCI_2",
    "NR_UE_Nbr_PCI_3",
]

with col_2:
    selected_pci_list = st.multiselect("Choose Cell Id:", coverages["PCI"])

    start_n, end_n = st.select_slider(
        "Select the range of neighbor cells to include",
        options=[0, 1, 2, 3, 4],
        value=(0, 0),
    )

coverages = coverages[coverages["PCI"].isin(selected_pci_list)]

mask = False

for col in columns_to_check[start_n : end_n + 1]:
    mask |= gdf[col].isin(selected_pci_list)

gdf = gdf[mask]

folium.GeoJson(
    coverages.clipped_coverage,
    style_function=lambda x: {
        "fillColor": "red",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.2,
    },
).add_to(m)

folium.GeoJson(
    gdf,
    marker=folium.Circle(
        radius=10,
        fill=True,
        fill_color="blue",
        fill_opacity=0.2,
        color="black",
        weight=1,
    ),
).add_to(m)

with col_1:
    st_folium(m, height=500, use_container_width=True)
