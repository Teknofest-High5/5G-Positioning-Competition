import numpy as np
import pandas as pd
from geopy.distance import geodesic

# -------------------------------------------------------------
# 1) VERİCİ (Tx) VE ALICI (Rx) BİLGİLERİ
# -------------------------------------------------------------

def calculate_coverage(
        tx_lat, 
        tx_lon, 
        rx_lat, 
        rx_lon, 
        azimuth_deg, 
        tx_height_m, 
        h_bw_deg,
        v_bw_deg,
        tx_power_dbm = 17.91, #Synchronization Signal Block, Verici antenden çıkan sinyalin gücü, dbm cinsindinden
        rx_height_m = 0,
        eta = 0.77, # Anten verimliliği (0–1)
        n_tx = 64, # 64T64R => 64 Tx elemanı (beamforming)
        downtilt_fixed_deg = -6, 
        ):
    
    # -------------------------------------------------------------
    # 2) ANTEN KAZANCI: Beamwidth ve eta'ya göre
    # -------------------------------------------------------------              

    # ► 2-a) Beamwidth'e dayalı element/panel kazancı (dBi)
    solid_angle_deg2 = 4 * np.pi * (180 / np.pi) ** 2       # 4π·(180/π)^2 ≈ 41253
    g_element_db = 10 * np.log10((solid_angle_deg2 * eta) / (h_bw_deg * v_bw_deg))

    # ► 2-b) Beamforming (array) kazancı (dB)
    g_bf_db = 10 * np.log10(n_tx)    # Ideal coherent gain

    # ► 2-c) Maksimum (boresight) anten kazancı
    max_ant_gain_db = g_element_db + g_bf_db

    #https://www.nature.com/articles/s41598-025-93251-7
    #https://www.qsl.net/n1bwt/app-6a.pdf
    # -------------------------------------------------------------
    # 3) JEODEZİK MESAFE VE AÇI HESAPLAMALARI
    # -------------------------------------------------------------
    tx_coords = (tx_lat, tx_lon)
    rx_coords = (rx_lat, rx_lon)

    horiz_dist = geodesic(tx_coords, rx_coords).meters
    dz         = tx_height_m - rx_height_m
    dist_3d    = np.hypot(horiz_dist, dz)

    dy = (rx_lat - tx_lat) * 111_000     # ≈111 km / ° latitude
    dx = (rx_lon - tx_lon) *  85_000     # İstanbul ≈85 km / ° longitude

    az_to_rx = (np.degrees(np.arctan2(dy, dx)) + 360) % 360 # yatay yönlü açı
    el_to_rx = np.degrees(np.arctan2(dz, horiz_dist)) # dikey yönlü açı

    # -------------------------------------------------------------
    # 4) ANTEN KAZANÇ (cos² MODELİ)
    # -------------------------------------------------------------
    def cos2_gain(az_beam, az_target, el_beam, el_target, g_max_db):
        """
        az_beam   : Antenin baktığı azimut (°)
        az_target : Rx'in göreceli azimut açısı (°)
        el_beam   : Antenin baktığı elevasyon (°)
        el_target : Rx'in göreceli elevasyon açısı (°)
        g_max_db  : Boresight'taki maksimum kazanç (dBi)
        """
        d_az = np.abs((az_beam - az_target + 180) % 360 - 180) # antenin yatayda kullanıcıya olan açısı
        d_el = np.abs(el_beam - el_target) # antenin dikeyde kullanıcıya olan açısı
        gain_lin = np.maximum(np.cos(np.radians(d_az)), 0)**2 * \
                np.maximum(np.cos(np.radians(d_el)), 0)**2
        return g_max_db + 10 * np.log10(gain_lin + 1e-12)   # numerical safety

    tx_gain_db = cos2_gain(azimuth_deg, az_to_rx,
                        downtilt_fixed_deg, el_to_rx,
                        max_ant_gain_db)

    # https://www.mathworks.com/help/phased/ug/cosine-antenna-element.html

    # -------------------------------------------------------------
    # 5) PATH LOSS (FSPL + ZEMİN YANSIMASI)
    # -------------------------------------------------------------
    carrier_hz = 3.5e9  # 3.5 GHz
    # https://www.scribd.com/document/669032517/AirScale-MAA-64T64R-192AE-n78-200-W-AEQI
    c = 3e8
    lam = c / carrier_hz # dalga boyu
    fspl_db = 20 * np.log10(4 * np.pi * dist_3d / lam) #Free Space Path Loss
    # https://en.wikipedia.org/wiki/Free-space_path_loss

    d_reflect = np.hypot(horiz_dist, tx_height_m + rx_height_m) # yansıyan ışının gittiği yol

    k = 2 * np.pi / lam  # Dalga sayısı
    r1 = dist_3d         # Doğrudan yol uzunluğu
    r2 = d_reflect       # Yansıyan yol uzunluğu
    Gamma = 1            # Yansıma katsayısı (varsayılan olarak 1 alınır)

    # Yansıyan sinyal ile doğrudan gelen sinyal arasında kaç derecelik faz farkı var?
    # https://en.wikipedia.org/wiki/Two-ray_ground-reflection_model
    E_total = (1 / r1) * np.exp(-1j * k * r1) + Gamma * (1 / r2) * np.exp(-1j * k * r2)

    corr_db = 20 * np.log10(np.abs(E_total) + 1e-12)  # yansımadan kaynaklı kazanç ya da kayıp
    path_loss_db = fspl_db - corr_db

    # -------------------------------------------------------------
    # 6) RSRP VE TIMING ADVANCE
    # -------------------------------------------------------------
    rx_power_dbm = tx_power_dbm + tx_gain_db - path_loss_db
    delay_s = dist_3d / c
    timing_advance = int(delay_s / 5.2e-7)

    # -------------------------------------------------------------
    # 7) ÇIKTI
    # -------------------------------------------------------------
    out = pd.DataFrame([{
        "Tx (lat,lon)"   : f"{tx_lat:.6f}, {tx_lon:.6f}",
        "Rx (lat,lon)"   : f"{rx_lat:.6f}, {rx_lon:.6f}",
        "3D Dist (m)"    : round(dist_3d, 2),
        "Downtilt (°)"   : downtilt_fixed_deg,
        "el_to_rx (°)"   : round(el_to_rx, 2),
        "Ant Gain (dBi)" : round(tx_gain_db, 2),
        "NR_UE_Pathloss_DL_0" : round(path_loss_db, 2),
        "NR_UE_RSRP_0"     : round(rx_power_dbm, 2),
        "NR_UE_Timing_Advance"     : timing_advance
    }])

    #print(out.to_string(index=False))
    return out
