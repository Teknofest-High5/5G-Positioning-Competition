# **Sözlüğümüz**

| **Anahtar Kelimeler** | **Açıklamalar** |
|:------------------------------|:--------------------------------------------|
| Herhangi bir <br> key bilgi olabilir | Buraya açıklamalar eklenecek <br> Bir alt satıra geçmek için `<br>` komutunu kullanabilirsiniz |
| **Kabinet** | Baz istasyonunun kabin numarası veya ismi. Toplantıda bir etkisi olmadığı söylendi. |
| **Sector** | Baz istasyonunun belirli bir yönü kapsayan sektörü. Aynı kabinde birden fazla sektör olabilir, her biri farklı yönlere hizmet eder. Yönlü antenler olarak düşünebiliriz. |
| **Cell Name** | Hücre adı, yani belirli bir baz istasyonu sektörüne ait hücrenin benzersiz ismi. |
| **Latitude** | Hücrenin bulunduğu konumun enlem (y) koordinatı. |
| **Longitude** |  Hücrenin bulunduğu konumun boylam (x) koordinatı. |
| **Azimuth [°]** | Hücrenin yaydığı sinyalin yönü (coğrafi kuzeye göre açı, derece cinsinden). Örneğin, 0° kuzeyi, 90° doğuyu, 180° güneyi, 270° batıyı gösterir. |
| **Horizontal Beamwidth [°]** | Antenin yatayda yaydığı sinyalin genişliği (derece cinsinden). Daha yüksek değerler, daha geniş kapsama alanı sağlar. |
| **Vertical Beamwidth [°]** | Antenin dikeyde yaydığı sinyalin genişliği (derece cinsinden). Daha düşük değerler, sinyalin daha odaklı olduğunu gösterir. |
| **Height [m]** | Antenin yerden yüksekliği (metre cinsinden). |
| **MIMO** |**Multiple Input Multiple Output** - Hücrenin anten yapılandırması. 64T64R ifadesi, 64 gönderici (Transmit) ve 64 alıcı (Receive) anten olduğunu belirtir. |
| **PCI** | **Physical Cell ID** - Fiziksel hücre kimliği. Mobil cihazların hücreleri tanımlamak için kullandığı benzersiz bir kimlik numarasıdır.|
| **rachroot** | **Random Access Channel (RACH) root sequence index** - Mobil cihazların ağa erişirken kullandığı kök dizilim numarasıdır. Hücre bazlı erişim sürecinde kullanılır. |
| **Power [W]** | Hücrenin yayın yaptığı toplam güç (Watt cinsinden). Daha yüksek güç, daha geniş kapsama alanı ve daha iyi sinyal kalitesi anlamına gelir. Bizim verimizde hepsi 200. |
| **Ssbpower [dBm]** | **Synchronization Signal Block (SSB) power**. Mobil cihazların hücreyi algılaması için gönderilen senkronizasyon sinyalinin gücü (desibel-miliwatt cinsinden). Bizim verimizde hepsi 17.91 |

**MIMO**
Kablosuz haberleşme sistemlerinde veri hızını ve bağlantı kalitesini artırmak için kullanılan bir yöntemdir. 64T64R ve 32T32R gibi ifadeler, baz istasyonunun kaç verici (T - Transmit) ve kaç alıcı (R - Receive) antene sahip olduğunu gösterir.

**64T64R** -> 64T64R, baz istasyonunda 64 verici (Transmit) ve 64 alıcı (Receive) anten olduğunu gösterir. Bu sistem, aynı anda 64 farklı sinyal akışını destekleyebilir. 5G baz istasyonlarında ve yoğun veri trafiği olan bölgelerde tercih edilir.

**32T32R** -> 32T32R, 32 verici ve 32 alıcı antene sahip bir MIMO sistemi anlamına gelir. Kapsama alanı ve kapasite dengesi daha uygun olduğu için daha az yoğun bölgelerde kullanılabilir.

64T64R büyük şehirlerde ve yoğun kullanım alanlarında kullanılırken, 32T32R daha az yoğun bölgeler için uygundur.

Eğer bir ağın yüksek bant genişliği ve hızlı bağlantı sunması isteniyorsa, 64T64R gibi yüksek anten yapılandırmaları tercih edilir.



---
