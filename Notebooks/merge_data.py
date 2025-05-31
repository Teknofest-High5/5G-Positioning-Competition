import polars as pl
import numpy as np
from path_config import PathConfig

paths = PathConfig()


def merge_datasets(
    data: pl.DataFrame,
    test_data: pl.DataFrame,
    drop_cols: list = ["Distance", "GPS_Confidence", "Message", "Technology_Mode"],
    create_file: bool = False,
    path: PathConfig = paths._processed_saha_olcum_dir,
    file_suffix: str = None,
):
    common_cols = set(data.columns) & set(test_data.columns)
    cast_exprs = [pl.col(col).cast(pl.String, strict=False) for col in common_cols]
    data = data.with_columns(cast_exprs)
    test_data = test_data.with_columns(cast_exprs)

    merged_data = pl.concat([data, test_data], how="diagonal").drop(drop_cols)
    merged_data = merged_data.drop_nulls(subset=["Latitude", "Longitude"])

    pci_cols = [col for col in merged_data.columns if "PCI" in col]
    rsrp_cols = [col for col in merged_data.columns if "RSRP" in col]

    merged_data = merged_data.with_columns(
        [pl.col(col).cast(pl.Int64, strict=False) for col in pci_cols]
        + [pl.col(col).cast(pl.Float64, strict=False) for col in rsrp_cols]
    )

    if create_file:
        merged_data.write_parquet(path / f"merged_data_{file_suffix}.parquet")

    return merged_data


if __name__ == "__main__":
    dl_data = pl.read_excel(paths.dl_path, sheet_name="Series Formatted Data")
    dl_test_data = pl.read_excel(paths.test_dl_path, sheet_name="Series Formatted Data")

    ul_data = pl.read_excel(paths.ul_path, sheet_name="Series Formatted Data")
    ul_test_data = pl.read_excel(paths.test_ul_path, sheet_name="Series Formatted Data")

    merge_datasets(dl_data, dl_test_data, create_file=True, file_suffix="dl")
    merge_datasets(ul_data, ul_test_data, create_file=True, file_suffix="ul")
