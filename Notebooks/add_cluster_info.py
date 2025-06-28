# create folds with agglomerative clustering and save folds as a pickle file.
import os
import pickle
import polars as pl
import geopandas as gpd
from sklearn.metrics.pairwise import haversine_distances
from sklearn.cluster import AgglomerativeClustering
from pyproj import Geod

geod = Geod(ellps="WGS84")

df = pl.read_parquet("data/parquet/processed/dl.parquet")
df_clean = df.drop_nulls(subset=["Longitude", "Latitude"]).select(
    pl.col("Longitude").radians(), pl.col("Latitude").radians(), "Message"
)

n_clusters = 10
X = df_clean[["Latitude", "Longitude"]].to_numpy()

agg = AgglomerativeClustering(
    n_clusters=n_clusters, metric=haversine_distances, linkage="complete"
)
agg.fit_predict(X)

complete = df.join(
    df_clean.with_columns(pl.Series(name="cluster", values=agg.fit_predict(X))).select(
        "cluster", "Message"
    ),
    on="Message",
    how="left",
)

complete.write_parquet("data/parquet/processed/dl.with_cluster.parquet")

cluster_centers = {}

for cluster in range(n_clusters):
    df_filtered = complete.select("Longitude", "Latitude", "cluster").filter(
        (pl.col("cluster") == cluster)
    )

    geometry = gpd.points_from_xy(
        df_filtered["Longitude"], df_filtered["Latitude"], crs="EPSG:4326"
    )
    gdf = gpd.GeoDataFrame(geometry=geometry)
    gdf = gdf.to_crs(
        "EPSG:32635"
    )  # projecting to local UTM zone for accurate centroid calculation.
    centroid = gdf.union_all().centroid
    centroid_gdf = gpd.GeoDataFrame(geometry=[centroid], crs="EPSG:32635").to_crs(
        "EPSG:4326"
    )  # converting centroid back
    centroid = centroid_gdf.geometry.x.iloc[0], centroid_gdf.geometry.y.iloc[0]
    cluster_centers[cluster] = centroid

# print(f"clusters and cluster centroids:\n{cluster_centers}")

distance_dict = {}
distance_threshold = 700

for i in range(len(cluster_centers)):
    lon1, lat1 = cluster_centers[i]
    for j in range(i + 1, len(cluster_centers)):
        lon2, lat2 = cluster_centers[j]
        _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
        if distance_threshold < distance:
            distance_dict[(i, j)] = distance

# print(f"distance between fold centers:\n{distance_dict}")

folds = {}

for pairs in distance_dict:
    if pairs[0] not in folds:
        folds[pairs[0]] = [pairs[1]]
    else:
        folds[pairs[0]].append(pairs[1])
    if pairs[1] not in folds:
        folds[pairs[1]] = [pairs[0]]
    else:
        folds[pairs[1]].append(pairs[0])


# deleting folds where test fold size > train fold size

del_folds = False
if del_folds:    
    for fold in folds.copy():
        test_cluster = fold
        train_clusters = folds[fold]

        test_size = len(complete.filter(pl.col("cluster") == test_cluster))
        train_size = len(complete.filter(pl.col("cluster").is_in(train_clusters)))

        if test_size > train_size:
            del folds[fold]

os.makedirs("data/folds", exist_ok=True)

with open("data/folds/folds.pkl", "wb") as f:
    pickle.dump(folds, f)

# print(f"folds:\n{folds}")

# plot clusters if you want to check
"""
df = pl.read_parquet("data/parquet/processed/dl.with_cluster.parquet")

plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    df["Longitude"],
    df["Latitude"],
    c=df["cluster"],
    cmap="tab10",
    s=10,           
)

for cluster_id, (lon, lat) in cluster_centers.items():
    plt.scatter(lon, lat, c="red", marker="o", s=100)
    plt.text(lon, lat, str(cluster_id), color="black", fontsize=15, ha="center")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.show()
"""
