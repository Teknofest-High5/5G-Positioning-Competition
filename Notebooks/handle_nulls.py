import polars as pl
from calculations_util.distance import pathloss_to_distance

cell_data = pl.read_parquet("data/parquet/cell_info.parquet")
df = pl.read_parquet("data/parquet/dl.parquet").sort("Message")


df_flags = (
    df.select(
        "Time",
        "NR_UE_RRCHOAttempt",
        "NR_UE_RRCHOOK",
        "NR_UE_RACH_OK",
        "NR_UE_RACH_Attempt",
    )
    .group_by("Time")
    .agg(
        [
            (pl.col("NR_UE_RACH_Attempt") == 1)
            .any()
            .cast(pl.Int8)
            .alias("rach_attempt"),
            (pl.col("NR_UE_RACH_OK") == 1).any().cast(pl.Int8).alias("rach_ok"),
            (pl.col("NR_UE_RRCHOAttempt") == 1).any().cast(pl.Int8).alias("ho_attempt"),
            (pl.col("NR_UE_RRCHOOK") == 1).any().cast(pl.Int8).alias("ho_ok"),
        ]
    )
)

fill_cols = [
    "NR_UE_Timing_Advance",
    "NR_UE_Pathloss_DL_0",
    "NR_UE_Throughput_PDCP_DL",
    "App_Throughput_DL",
    "NR_UE_NACK_Rate_DL_0",
    "NR_UE_Ack_As_Nack_DL_0",
    "NR_UE_MCS_DL_0",
    "NR_UE_RB_Num_DL_0",
    "NR_UE_Modulation_Avg_DL_0",
    "NR_UE_RI_DL_0",
    "NR_UE_BLER_DL_0",
    "NR_UE_CCE_AggregationLev_0",
    "NR_UE_Power_Tx_PUSCH_0",
    "NR_UE_Power_Tx_PRACH_0",
    "NR_UE_NACK_Rate_UL_0",
]

df = df.with_columns([
    pl.col(col).forward_fill().backward_fill().over("Time").alias(col)
    for col in fill_cols
])

df = df.filter(
    pl.col("NR_RRC_MsgType").is_null()
).drop(
    [
        "NR_UE_RRCHOAttempt",
        "NR_UE_RRCHOOK",
        "NR_UE_RACH_OK",
        "NR_UE_RACH_Attempt",
        "NR_RRC_MsgType",
    ]
)

group_cols = [
    "Longitude",
    "Latitude",
    "Time",
    "NR_UE_PCI_0",
    "NR_UE_RSRP_0",
    "NR_UE_RSRQ_0",
    "NR_UE_SINR_0",
    "NR_UE_Nbr_PCI_0",
    "NR_UE_Nbr_PCI_1",
    "NR_UE_Nbr_PCI_2",
    "NR_UE_Nbr_PCI_3",
    "NR_UE_Nbr_RSRP_0",
    "NR_UE_Nbr_RSRP_1",
    "NR_UE_Nbr_RSRP_2",
    "NR_UE_Nbr_RSRP_3",
    "NR_UE_Nbr_RSRQ_0",
    "NR_UE_Nbr_RSRQ_1",
    "NR_UE_Nbr_RSRQ_2",
    "NR_UE_Nbr_RSRQ_3",
]

df = (
    df.group_by(group_cols)
    .agg(
        pl.col("Message").max(), *[pl.col(col).first().alias(col) for col in fill_cols]
    )
    .join(df_flags, on="Time")
    .drop("Time")
    .filter(pl.col("NR_UE_PCI_0").is_in(list(cell_data["PCI"])),
            pl.col("NR_UE_PCI_0").is_not_null(),
            pl.col("NR_UE_RSRP_0").is_not_null())
)

# replacing with bit/symbol

df = df.with_columns(
    [
        pl.when(pl.col("NR_UE_Modulation_Avg_DL_0") == "QPSK")
        .then(4)
        .when(pl.col("NR_UE_Modulation_Avg_DL_0") == "16QAM")
        .then(16)
        .when(pl.col("NR_UE_Modulation_Avg_DL_0") == "64QAM")
        .then(64)
        .when(pl.col("NR_UE_Modulation_Avg_DL_0") == "256QAM")
        .then(256)
        .otherwise(None)
        .alias("modulation_avg_encoded"),
    ]
)

df = df.with_columns(
    [pl.col("modulation_avg_encoded").log(base=2).alias("modulation_avg_log2_bits")]
)

df = df.with_columns(
    [
        pl.when(pl.col("NR_UE_CCE_AggregationLev_0") == "LEVEL_1")
        .then(1)
        .when(pl.col("NR_UE_CCE_AggregationLev_0") == "LEVEL_2")
        .then(2)
        .when(pl.col("NR_UE_CCE_AggregationLev_0") == "LEVEL_4")
        .then(4)
        .when(pl.col("NR_UE_CCE_AggregationLev_0") == "LEVEL_8")
        .then(8)
        .when(pl.col("NR_UE_CCE_AggregationLev_0") == "LEVEL_16")
        .then(16)
        .otherwise(None)
        .alias("cce_level_encoded")
    ]
)

df = df.with_columns(
    [
        pl.col("NR_UE_MCS_DL_0")
        .str.extract(r"^(\d+)", group_index=1)  # extracting mcs index at the beggining
        .cast(pl.Int64)
        .alias("mcs_index")
    ]
)

df = df.with_columns(
    pathloss_to_distance(pl.col("NR_UE_Pathloss_DL_0")).alias("pl_distance")
)

df = df.with_columns(
    [
        (pl.col("NR_UE_Pathloss_DL_0") / pl.col("pl_distance")).alias("pl_per_meter"),
        (pl.col("pl_distance").log1p().alias("log1p_pl_distance")),
        (pl.col("App_Throughput_DL") / pl.col("NR_UE_RB_Num_DL_0")).alias(
            "spectral_efficiency"
        ),
        (pl.col("modulation_avg_log2_bits") / (pl.col("NR_UE_RB_Num_DL_0"))).alias(
            "modulation_efficiency"
        ),
        (pl.col("NR_UE_Throughput_PDCP_DL") / pl.col("pl_distance")).alias(
            "throughput_per_meter"
        ),
        (pl.col("NR_UE_SINR_0") / (pl.col("pl_distance"))).alias("sinr_per_meter"),
        (pl.col("NR_UE_SINR_0") / (pl.col("NR_UE_RSRP_0"))).alias("sinr_over_rsrp"),
        (pl.col("NR_UE_RSRP_0") - pl.col("NR_UE_Nbr_RSRP_0")).alias("rsrp_delta"),
        (pl.col("NR_UE_RSRQ_0") - pl.col("NR_UE_Nbr_RSRQ_0")).alias("rsrq_delta"),
        (pl.col("NR_UE_RSRP_0") / pl.col("NR_UE_Pathloss_DL_0")).alias(
            "signal_loss_ratio"
        ),
    ]
)

df.write_parquet("data/parquet/processed/dl.parquet")
