# Merging new dataset provided by teknofest
import polars as pl

dl_data = pl.read_excel("data/5g-field-data/5G_DL.xlsx", sheet_name="Series Formatted Data")
dl_test_data = pl.read_excel("data/5g-field-data/test-data/5G_DL.xlsx", sheet_name="Series Formatted Data")

dl_test_data = dl_test_data.with_columns((pl.col("Message")+ dl_data["Message"][-1] + 1))

for col in dl_data.columns:
    if col not in dl_test_data.columns:
        dl_data = dl_data.drop(col)

for col in dl_test_data.columns:
    if col not in dl_data.columns:
        dl_test_data = dl_test_data.drop(col)

cat_cols = [
    "NR_UE_PCI_0",
    "NR_UE_Nbr_PCI_0",
    "NR_UE_Nbr_PCI_1",
    "NR_UE_Nbr_PCI_2",
    "NR_UE_Nbr_PCI_3",
    "NR_UE_RI_DL_0",
    "NR_UE_Modulation_Avg_DL_0",
    "NR_UE_MCS_DL_0",
    "NR_UE_CCE_AggregationLev_0",
    "NR_RRC_MsgType",
    "NR_UE_RRCReEst_EndResult",
    "NAS_5GS_MM_MessageType"
]

merged_data = pl.concat([dl_data,dl_test_data],how='vertical_relaxed')

merged_data = merged_data.drop("Technology_Mode")

for col in merged_data.columns:
    if col == "Time":
        continue
    elif "_PCI_" in col:
        merged_data = merged_data.with_columns(
            pl.col(col).cast(pl.Float64, strict=True)
        )
    elif (merged_data[col].dtype == pl.String) and col not in cat_cols:
        merged_data = merged_data.with_columns(
            pl.col(col).cast(pl.Float64, strict=True)
        )

merged_data.write_parquet("data/parquet/dl.parquet")