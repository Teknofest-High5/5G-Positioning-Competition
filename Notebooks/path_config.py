from pathlib import Path
import os

class PathConfig:
    def __init__(self, base_dir= None):
        if base_dir is None:
            self._base_dir = Path("..").resolve()
        else:
            self._base_dir = Path(base_dir).resolve()
        
        self._data_dir = self._base_dir / "Data"
        self._raw_dir = self._data_dir / "Raw"
        self._processed_dir = self._data_dir / "Processed"

        self._raw_konfigurasyon_dir = self._data_dir / self._raw_dir / "5G Baz İstasyonu Konfigürasyon Verileri"
        self._raw_saha_olcum_dir = self._data_dir / self._raw_dir / "5G Saha Ölçüm Verileri (GPS mevcut)"
        self._raw_harita_dir = self._data_dir / self._raw_dir / "İTÜ Kampüs Harita Verileri"
        self.test_data_dir = self._raw_dir / "Test Verisi"

        self._processed_konfigurasyon_dir = self._data_dir / self._processed_dir / "Base_Stations_Data"
        self._processed_saha_olcum_dir = self._data_dir / self._processed_dir / "DL_UL_Scanner"
        self._processed_harita_dir = self._data_dir / self._processed_dir / "Map_Data"
        self._processed_measured_coverage_dir = self._processed_harita_dir / "Measured Coverage"
        self._processed_coverage_dir = self._processed_harita_dir / "Calculated Coverage"
        self._processed_other_dir = self._data_dir / self._processed_dir / "Other"

        self.Hucre_Bilgileri = self._raw_konfigurasyon_dir / "İTÜ 5G Hücre Bilgileri.xlsx"

        self.kabinets_path = self._processed_saha_olcum_dir / "Kabinets.csv"

        self.dl_path = self._raw_saha_olcum_dir / "5G_DL.xlsx"
        self.ul_path = self._raw_saha_olcum_dir / "5G_UL.xlsx"
        self.scanner_path = self._raw_saha_olcum_dir / "5G_Scanner.xlsx"

        self.test_dl_path = self.test_data_dir / "5G_DL.xlsx"
        self.test_ul_path = self.test_data_dir / "5G_UL.xlsx"
        self.test_scanner_path = self.test_data_dir / "5G_Scanner.xlsx"

        self.build_path = self._raw_harita_dir / "ITU_3DBINA_EPSG4326.shp"
        self.vege_path = self._raw_harita_dir / "ITU_3DVEGETATION_EPSG4326.shp"
        self.waters_path = self._raw_harita_dir / "ITU_SUKUTLESI_EPSG4326.shp"
        self.border_path = self._raw_harita_dir / "ITU_SINIRDUVAR_EPSG4326.shp"
        self.roads_path = self._raw_harita_dir / "ITU_ULASIMAGI_EPSG4326.shp"

        # sadece şu ana kadar kullandığımız harita dosylarını koydum,
        # diğer harita dosyaları için de aynı şekilde path tanımlayabilirsin.

        self.parquet_data = self._processed_saha_olcum_dir / "5G_DataSet.parquet"
        self.train_df_path = self._processed_saha_olcum_dir / "y_train.csv"
        self.test_df_path = self._processed_saha_olcum_dir / "y_test.csv"
        self.predictions_df_path = self._processed_saha_olcum_dir / "predictions.csv"
