from itertools import combinations
from shapely.ops import unary_union
import geopandas as gpd

coverages = gpd.read_parquet("data/parquet/coverages/coverages.parquet")
coverages["clipped_coverage"] = coverages.clipped_coverage.to_crs("EPSG:32635")

intersections_2 = []

for cell_1, cell_2 in combinations(coverages["PCI"], 2):
    coverage_poly_1 = coverages[coverages["PCI"] == cell_1].clipped_coverage.iloc[0]
    coverage_poly_2 = coverages[coverages["PCI"] == cell_2].clipped_coverage.iloc[0]

    intersection = coverage_poly_1.intersection(coverage_poly_2)

    if intersection.is_empty:
        convex_hull_flag = 1
        combined = unary_union([coverage_poly_1, coverage_poly_2])
        convex_hull = combined.convex_hull
        area = convex_hull.area
        shape = convex_hull

    else:
        convex_hull_flag = 0
        area = intersection.area
        shape = intersection

    intersections_2.append(
        {
            "sorted_cell_pairs": sorted([cell_1,cell_2]),
            "convex_hull": convex_hull_flag,
            "area_m2": area,
            "geometry": shape,
        }
    )

intersections_2 = gpd.GeoDataFrame(intersections_2, geometry="geometry", crs="EPSG:32635")
intersections_2["centroid"] = intersections_2.geometry.centroid.to_crs("EPSG:4326")
intersections_2 = intersections_2.to_crs("EPSG:4326")

intersections_2.to_parquet("data/parquet/coverages/coverages_intersect_2.parquet")
