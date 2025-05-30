import pandas as pd
from path_config import PathConfig
paths = PathConfig()

kabinets = [
    {
        "Kabinet": "WITUFERG",
        "Sector": "AAS-S1CB",
        "Latitude": 41.1073413,
        "Longitude": 29.0233668,
        "Azimuth": 50,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 10,
        "Height": 10,
        "MIMO": "64T64R",
        "PCI": 30,
        "rachroot": 26,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUFERG",
        "Sector": "AAS-S2CB",
        "Latitude": 41.1070873,
        "Longitude": 29.0226646,
        "Azimuth": 260,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 10,
        "Height": 10,
        "MIMO": "64T64R",
        "PCI": 40,
        "rachroot": 126,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUFERG",
        "Sector": "AAS-S3CB",
        "Latitude": 41.1080861,
        "Longitude": 29.028122,
        "Azimuth": 230,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 10,
        "Height": 6,
        "MIMO": "64T64R",
        "PCI": 59,
        "rachroot": 42,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUFESG",
        "Sector": "AAS-S1CB",
        "Latitude": 41.1080861,
        "Longitude": 29.0281222,
        "Azimuth": 110,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 10,
        "Height": 6,
        "MIMO": "64T64R",
        "PCI": 48,
        "rachroot": 69,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUFESG",
        "Sector": "AAS-S2CB",
        "Latitude": 41.1054694,
        "Longitude": 29.0278333,
        "Azimuth": 255,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 9.5,
        "Height": 18,
        "MIMO": "32T32R",
        "PCI": 68,
        "rachroot": 132,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUFESG",
        "Sector": "AAS-S3CB",
        "Latitude": 41.1054694,
        "Longitude": 29.0278333,
        "Azimuth": 340,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 9.5,
        "Height": 18,
        "MIMO": "32T32R",
        "PCI": 76,
        "rachroot": 75,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUPAG",
        "Sector": "AAS-S1CB",
        "Latitude": 41.1043417,
        "Longitude": 29.021747,
        "Azimuth": 300,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 10,
        "Height": 6,
        "MIMO": "64T64R",
        "PCI": 3,
        "rachroot": 30,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUPAG",
        "Sector": "AAS-S2CB",
        "Latitude": 41.1043417,
        "Longitude": 29.021747,
        "Azimuth": 40,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 10,
        "Height": 6,
        "MIMO": "64T64R",
        "PCI": 13,
        "rachroot": 130,
        "Power": 200,
        "Ssbpower": 17.91
    },
    {
        "Kabinet": "WITUPAG",
        "Sector": "AAS-S3CB",
        "Latitude": 41.1058417,
        "Longitude": 29.0205028,
        "Azimuth": 130,
        "Horizontal_Beamwidth": 65,
        "Vertical_Beamwidth": 10,
        "Height": 6,
        "MIMO": "64T64R",
        "PCI": 23,
        "rachroot": 93,
        "Power": 200,
        "Ssbpower": 17.91
    }
]

kabinets = pd.DataFrame(kabinets)
kabinets.to_csv(paths._processed_saha_olcum_dir / "kabinets.csv")