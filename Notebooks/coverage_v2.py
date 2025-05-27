import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_rsrp_and_heatmap(
    grid_data: pd.DataFrame,
    bs_longitude: float,
    bs_latitude: float,
    bs_height: float = 30,
    ue_height: float =0,
    azimuth: float = 0,
    digital_downtilt: float = 5,
    ssb_power: float = 17.91,
    carrier_freq_mhz: float = 3500,
    vertical_bw_deg: float = 10,
    horizontal_bw_deg: float = 65,
    sidelobe_suppression_db: float = 16,
    front_back_ratio_db: float = 25,
    plot_heatmap: bool = False,
    path_loss_strategy: str = "FSPL"
):
    
    dx = (grid_data['Longitude'] - bs_longitude) * 111320 * np.cos(np.radians(bs_latitude))
    dy = (grid_data['Latitude'] - bs_latitude) * 111320
    dz = ue_height-bs_height

    distance_3d = np.sqrt(dx**2 + dy**2 + dz**2)
    distance_2d = np.sqrt(dx**2 + dy**2)

    horizontal_angle = (np.degrees(np.arctan2(dx, dy)) - azimuth) % 360
    horizontal_angle = np.where(horizontal_angle > 180, 360 - horizontal_angle, horizontal_angle)

    vertical_angle = np.degrees(np.arctan2(-dz, distance_2d)) - digital_downtilt

    def gain(horizontal_bw_deg, vertical_bw_deg, horizontal_angle, vertical_angle, sidelobe_suppression_db, front_back_ratio_db):

        directivity = 41253/(horizontal_bw_deg*vertical_bw_deg)
        half_hbwd = horizontal_bw_deg/2
        half_vbwd = vertical_bw_deg/2 

        max_gain = 10*np.log10(directivity)

        gain_horizontal = np.maximum(-12 * (horizontal_angle / half_hbwd)**2, -front_back_ratio_db)
        gain_vertical = np.maximum(-12 * (vertical_angle / half_vbwd)**2, -sidelobe_suppression_db)

        return max_gain + gain_horizontal + gain_vertical

    total_gain = gain(horizontal_bw_deg, vertical_bw_deg, horizontal_angle, vertical_angle, sidelobe_suppression_db, front_back_ratio_db)

    def fspl(distance_3d, carrier_freq_mhz):
        d = np.maximum(distance_3d, 1) / 1000
        return 20*np.log10(d) + 20*np.log10(carrier_freq_mhz) + 32.44
    
    def gpp_umi_nlos(distance_3d, carrier_freq_mhz, ue_height):
        d = np.maximum(distance_3d, 10)
        return 13.54 + 39.08*np.log10(d) + 20*np.log10(carrier_freq_mhz) - 0.6*(ue_height - 1.5)
    
    def gpp_umi_los(distance_3d, carrier_freq_mhz, bs_height, ue_height):
        
        if ue_height == 0:
            ue_height = 1.5 # yükseklik girilmediğinde fonskiyonun patlamaması lokasyon yüksekliği 3gpp için yükseklik kabul edilen 1.5m ile değiştiriliyor.

        dbp = (bs_height*ue_height*carrier_freq_mhz*(1e6)) / (3e8)
        pl = np.where(distance_3d <= dbp, fspl(distance_3d, carrier_freq_mhz), fspl(dbp, carrier_freq_mhz) + 40*np.log10(np.maximum(distance_3d / dbp, 1e-9)))
        return pl

    if path_loss_strategy == "FSPL":
        path_loss = fspl(distance_3d, carrier_freq_mhz)
    elif path_loss_strategy == "3GPP_UMi_NLOS":
        path_loss = gpp_umi_nlos(distance_3d, carrier_freq_mhz, ue_height)
    elif path_loss_strategy == "3GPP_UMi_LOS":
        path_loss = gpp_umi_los(distance_3d, carrier_freq_mhz, bs_height, ue_height)

    elif path_loss_strategy == "ALL":
        grid_data['RSRP_dBm_FSPL'] = ssb_power + total_gain - fspl(distance_3d, carrier_freq_mhz)
        grid_data['RSRP_dBm_3GPP_UMi_NLOS'] = ssb_power + total_gain - gpp_umi_nlos(distance_3d, carrier_freq_mhz, ue_height)
        grid_data['RSRP_dBm_3GPP_UMi_LOS'] = ssb_power + total_gain - gpp_umi_los(distance_3d, carrier_freq_mhz, bs_height, ue_height)
        return grid_data

    rsrp = ssb_power + total_gain - path_loss
    grid_data['RSRP_dBm'] = rsrp

    if plot_heatmap:
        plt.figure(figsize=(10, 8))
        sc = plt.scatter(grid_data['Longitude'], grid_data['Latitude'], c=rsrp, cmap='viridis', s=10)
        plt.colorbar(sc, label='dBm')
        plt.title('RSRP Heatmap')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)
        plt.show()

    return grid_data