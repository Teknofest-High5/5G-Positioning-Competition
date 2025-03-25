**5G_DL (Downlink)**

Downlink (DL), baz istasyonundan (gönderici) mobil cihaza (alıcı) yapılan veri iletimini ifade eder.

Kullanıcıların 5G ağı üzerinden veri alırken yaşadığı deneyimi ölçmek için kullanılır.

# 5G Ölçüm Verileri Açıklamaları

| **Anahtar Kelime** | **Açıklama** |
|:-----------------------------|:--------------------------------------------|
| **Message** | Ölçümle ilgili mesaj bilgisi. |
| **Time** | Ölçümün alındığı zaman damgası. |
| **Longitude** | Ölçümün alındığı konumun boylam (x) koordinatı. |
| **Latitude** | Ölçümün alındığı konumun enlem (y) koordinatı. |
| **Technology_Mode** | Kullanılan teknoloji türü (örneğin, 5G Standalone - 5GSA). |
| **NR_UE_PCI_0** | Kullanıcı cihazının bağlı olduğu hücrenin Physical Cell ID (PCI) değeri. |
| **NR_UE_RSRP_0** | Reference Signal Received Power (RSRP) - Hücreden gelen referans sinyal gücü (dBm). |
| **NR_UE_RSRQ_0** | Reference Signal Received Quality (RSRQ) - Hücreden alınan referans sinyalin kalitesi. |
| **NR_UE_SINR_0** | Signal-to-Interference-plus-Noise Ratio (SINR) - Sinyal-gürültü oranı. Yüksek değerler daha iyi bağlantı kalitesini gösterir. |
| **NR_UE_Nbr_PCI_0-4** | Kullanıcının etrafındaki komşu hücrelerin PCI değerleri. |
| **NR_UE_Nbr_RSRP_0-4** | Komşu hücrelerin RSRP (sinyal gücü) değerleri. |
| **NR_UE_Nbr_RSRQ_0-4** | Komşu hücrelerin RSRQ (sinyal kalitesi) değerleri. |
| **NR_UE_Timing_Advance** | Cihazın baz istasyonuna olan tahmini mesafesi (zaman gecikmesine göre hesaplanır). |
| **NR_UE_Pathloss_DL_0** | Path Loss - Sinyalin kaybettiği güç miktarı (downlink için). |
| **NR_UE_Throughput_PDCP_DL** | PDCP Katmanı Downlink Veri Hızı - Kullanıcının aldığı veri hızını gösterir. |
| **App_Throughput_DL** | Kullanıcı cihazında çalışan uygulamanın ölçülen indirme hızı. |
| **NR_UE_NACK_Rate_DL_0** | Negative Acknowledgment (NACK) Rate - Cihazın tekrar gönderilmesini istediği paket oranı. |
| **NR_UE_Ack_As_Nack_DL_0** | Olumlu geri bildirim (ACK) yerine olumsuz geri bildirim (NACK) olarak algılanan paket oranı. |
| **NR_UE_MCS_DL_0** | Modulation and Coding Scheme (MCS) - Verinin iletilmesi için kullanılan modülasyon ve kodlama şeması (downlink için). |
| **NR_UE_RB_Num_DL_0** | Kullanıcının tahsis edilen Resource Block (RB) sayısı (downlink için). |
| **NR_UE_Modulation_Avg_DL_0** | Kullanılan ortalama modülasyon türü (örneğin QPSK, 16-QAM, 64-QAM, 256-QAM). |
| **NR_UE_BLER_DL_0** | Block Error Rate (BLER) - Alınan blokların hata oranı (downlink için). |
| **NR_UE_CCE_AggregationLev_0** | Control Channel Elements (CCE) Aggregation Level - Kontrol sinyali için kullanılan CCE sayısı. |
| **NR_UE_Power_Tx_PUSCH_0** | Power Transmission on Uplink Shared Channel (PUSCH) - Cihazın uplink kanalına gönderdiği güç seviyesi. |
| **NR_UE_Power_Tx_PRACH_0** | Power Transmission on Random Access Channel (PRACH) - Rastgele erişim kanalı üzerinden gönderilen güç seviyesi. |
| **NR_UE_NACK_Rate_UL_0** | Uplink kanalındaki NACK oranı. |
| **NR_UE_RACH_Attempt** | Kullanıcının Random Access Channel (RACH) erişim denemesi sayısı. |
| **NR_UE_RACH_OK** | RACH işlemi başarıyla tamamlanan bağlantı sayısı. |
| **NR_UE_RACH_Fail** | RACH işlemi başarısız olan bağlantı sayısı. |
| **NR_UE_RACH_Procedure_Count** | Gerçekleştirilen toplam RACH prosedürü sayısı. |
| **NR_UE_RRCReEstAttempt** | RRC Yeniden Kurulum Denemesi - Bağlantının kopması sonucu yapılan yeniden bağlantı girişimi sayısı. |
| **NR_UE_RRCReEstFail** | RRC yeniden kurulumunun başarısız olduğu denemeler. |
| **NR_UE_RRCReEst_EndResult** | RRC yeniden kurulumunun nihai sonucu. |
| **NR_UE_RRCConnectionAttempt** | RRC bağlantı kurulumu için yapılan girişim sayısı. |
| **NR_UE_RRCConnectionSetupOk** | RRC bağlantısının başarıyla tamamlandığı durumlar. |
| **NR_UE_RRCConnectionComplete** | RRC bağlantı işleminin tamamlandığını gösterir. |
| **NR_UE_RRCConnectionDrop** | RRC bağlantısının düştüğü durumlar. |
| **NR_UE_RRCHOAttempt** | Kullanıcı cihazının başka bir hücreye geçiş (handover) denemesi. |
| **NR_UE_RRCHOOK** | Handover işleminin başarıyla gerçekleşmesi. |
| **NR_RRC_MsgType** | RRC protokolü tarafından kullanılan mesaj türü. |
| **NAS_5GS_MM_MessageType** | 5G çekirdek ağına yönelik NAS (Non-Access Stratum) Mobility Management mesaj türü. |
| **NAS_5GS_SM_MessageType** | 5G çekirdek ağına yönelik NAS Session Management mesaj türü. |


---
