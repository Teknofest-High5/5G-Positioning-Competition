# RSRP ve RSRQ nedir?
**Referans Sinyalleri Alınan Güç (RSRP) ve Alınan Referans Sinyal Kalitesi (RSRQ)** , modern LTE ağları için sinyal seviyesi ve kalitesinin temel ölçüleridir. Hücresel ağlarda, bir mobil cihaz hücreden hücreye hareket edip hücre seçimi/yeniden seçimi ve geçişini gerçekleştirirken komşu hücrelerin sinyal gücünü/kalitesini ölçmek zorundadır. Devir teslim prosedüründe, LTE spesifikasyonu RSRP, RSRQ veya her ikisini kullanma esnekliği sağlar.

**RSRP** – Referans Sinyali Alınan Güç, RSSI tipi bir ölçümdür. Tam bant genişliğine ve dar banta yayılmış LTE Referans Sinyallerinin gücüdür. RSRP/RSRQ’yu algılamak için minimum -20 dB SINR (S-Synch kanalının) gereklidir.

**RSRQ** – Alınan Referans Sinyali Kalitesi: Aynı bant genişliği üzerinden ölçülen RSSI ve kullanılan Kaynak Bloklarının sayısı `(N) RSRQ = (N * RSRP) / RSSI`’yi de dikkate alan kalite. RSRQ, C/I tipi bir ölçümdür ve alınan referans sinyalinin kalitesini gösterir. RSRQ ölçümü, RSRP güvenilir bir geçiş veya hücre yeniden seçim kararı vermek için yeterli olmadığında ek bilgi sağlar.

# SINR nedir?
Bilgi teorisi ve telekomünikasyon mühendisliğinde, Sinyal-Girişim-artı-Gürültü Oranı (SINR) , ağlar gibi kablosuz iletişim sistemlerinde kanal kapasitesi (veya bilgi aktarım hızı) üzerinde teorik üst sınırlar vermek için kullanılan bir miktardır.

Kablolu iletişim sistemlerinde sıklıkla kullanılan SNR’ye benzer şekilde, SINR, belirli bir ilgi sinyalinin gücünün, girişim gücünün (tüm diğer girişim sinyallerinden gelen) ve bazı arka plan gürültülerinin gücünün toplamına bölünmesiyle tanımlanır. Gürültü teriminin gücü sıfır ise, SINR sinyal-parazit oranına (SIR) düşer. Tersine, sıfır girişim, SINR’yi, hücresel ağlar gibi kablosuz ağların matematiksel modellerini geliştirirken daha az kullanılan sinyal-gürültü oranına (SNR) düşürür.

**SINR , kablosuz bağlantıların kalitesini ölçmenin bir yolu olarak kablosuz iletişimde yaygın olarak kullanılır.** Tipik olarak, bir sinyalin enerjisi, kablosuz ağlarda yol kaybı olarak adlandırılan mesafe ile azalır. Tersine, kablolu ağlarda, gönderici veya verici ile alıcı arasında kablolu bir yolun varlığı, verilerin doğru şekilde alınmasını belirler. Bir kablosuz ağda, diğer faktörleri hesaba katmak gerekir (örneğin, arka plan gürültüsü, diğer eşzamanlı iletimin girişim gücü). SINR kavramı, bu yönün bir temsilini yaratmaya çalışır.

---

<br><br>

# RSRP ve RSRQ Değerleri

## RSRP (Reference Signal Received Power)

| RSRP Değeri | Sinyal Gücü | Tanım |
|------------|------------|--------|
| ≥ -80 dBm | Harika | Maksimum veri hızlarıyla güçlü sinyal |
| -80 dBm ila -90 dBm | İyi | İyi veri hızlarıyla güçlü sinyal |
| -90 dBm ila -100 dBm | Fakir için adil | Güvenilir veri hızları elde edilebilir, ancak kesintili marjinal veriler mümkündür. Bu değer -100'e yaklaştığında performans önemli ölçüde düşecektir. |
| ≤ -100 dBm | Sinyal yok | Bağlantı kesilmesi |

## RSRQ (Reference Signal Received Quality)

| RSRQ Değeri | Sinyal Kalitesi | Tanım |
|------------|----------------|--------|
| ≥ -10 dB | Harika | Maksimum veri hızlarıyla güçlü sinyal |
| -10 dB ila -15 dB | İyi | İyi veri hızlarıyla güçlü sinyal |
| -15 dB ila -20 dB | Fakir için adil | Güvenilir veri hızları elde edilebilir, ancak kesintili marjinal veriler mümkündür. Bu değer -20'ye yaklaştığında performans önemli ölçüde düşecektir. |
| ≤ -20 dB | Sinyal yok | Bağlantı kesilmesi |

# SINR

| SINR         | Sinyal gücü       | Tanım  |
|-------------|----------------|------------------------------|
| ≥ 20 dB    | Harika         | Maksimum veri hızlarıyla güçlü sinyal |
| 13 dB – 20 dB | İyi          | İyi veri hızlarıyla güçlü sinyal |
| 0 dB – 13 dB | Fakir için adil | Güvenilir veri hızları elde edilebilir, ancak kesintili marjinal veriler mümkündür. Bu değer 0’a yaklaştığında performans önemli ölçüde düşecektir. |
| ≤ 0 dB     | Sinyal yok     | Bağlantı kesilmesi |
