# 🌐 TEKNOFEST 2025 - 5G Konumlandırma Yarışması

## 📡 Proje Hakkında

Bu repo, TEKNOFEST 2025 kapsamında Turkcell tarafından düzenlenen "5G Konumlandırma Yarışması" için geliştirilen konumlandırma algoritması ve ilgili çalışmaları içermektedir. Projemiz, İstanbul Teknik Üniversitesi Ayazağa Yerleşkesindeki mevcut 5G şebekesi kullanılarak en doğru konumlamayı yapan modeli geliştirmeyi hedeflemektedir.

## 🎯 Yarışma Amacı

Yarışma, 5G şebeke performans metrikleri ve GPS koordinat verilerini kullanarak en hassas konum tespitini yapabilecek modellerin geliştirilmesini amaçlamaktadır. Yarışmacı takımlar, radyo şebeke performans metrikleri ile GPS verilerini içeren şebeke ölçümlerine ait veri setleri üzerinden yapay zekâ, makine öğrenmesi veya farklı tekniklere dayalı konum tahminleme modelleri geliştirerek verilen hedef noktaları bulmaya çalışacaklardır.

## 👥 Takım Üyeleri

- Tarık Tuna Taşaltı - Takım Lideri - [E-posta]
- Osman Tekdamar - Üye - [E-posta]
- Elif Öznur Yeşil - Üye - [E-posta]
- Abdulkadir Temizoğlu - Üye - [E-posta]
- Kutay Doğan - Üye dogank20@itu.edu.tr

## 💻 Kullanılan Teknolojiler

- Python 3.x
- scikit-learn
- TensorFlow/PyTorch
- pandas
- NumPy
- Matplotlib
- [Diğer Kütüphaneler ve Araçlar]

## 📂 Repo Yapısı

```
.
├── data/                # Veri setleri (test ve eğitim verileri)
├── models/              # Eğitilmiş modeller
├── notebooks/           # Jupyter notebookları (veri analizi, model geliştirme)
├── src/                 # Kaynak kodlar
│   ├── preprocessing/   # Veri ön işleme modülleri
│   ├── features/        # Özellik çıkarımı
│   ├── models/          # Model tanımlamaları
│   └── utils/           # Yardımcı fonksiyonlar
├── reports/             # Raporlar ve sunumlar
│   ├── ön_tasarım/      # Ön tasarım raporu
│   └── final_tasarım/   # Final tasarım raporu
├── README.md            # Proje açıklaması
├── requirements.txt     # Bağımlılıklar
└── main.py              # Ana uygulama
```

## 🚀 Kurulum ve Çalıştırma

1. Repo'yu klonlayın:
```bash
git clone https://github.com/osman-tkdmr/5G-Positioning-Competition.git
cd 5G-Positioning-Competition
```

2. Gerekli bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. Veri setlerini hazırlayın:
```bash
python src/preprocessing/prepare_data.py
```

4. Modeli eğitin:
```bash
python src/models/train_model.py
```

5. Konumlandırma algoritmasını çalıştırın:
```bash
python main.py
```

## 📊 Metodoloji

Projemiz aşağıdaki adımları içermektedir:

1. **Veri Analizi**: 5G ölçüm verilerinin kapsamlı analizi
2. **Veri Ön İşleme**: Gürültü temizleme, normalizasyon ve özellik seçimi
3. **Model Geliştirme**: Çeşitli makine öğrenmesi ve derin öğrenme modellerinin geliştirilmesi ve test edilmesi
4. **Optimizasyon**: Model parametrelerinin ve hiperparametrelerinin optimizasyonu
5. **Test ve Doğrulama**: Farklı ortam koşullarında modelin doğruluğunun ve hassasiyetinin test edilmesi

## 📅 Yarışma Takvimi

- **Son Başvuru Tarihi**: 1 Mart 2025
- **5G Şebeke Test Verisinin Teslimi**: 14 Mart 2025
- **Bilgilendirme ve Soru-Cevap Seansı**: 17-21 Mart 2025
- **Ön Tasarım Raporu Teslim Tarihi**: 18 Nisan 2025, 17:00
- **Rapor Değerlendirme Sonuçlarının Açıklanması**: 16 Mayıs 2025
- **Takımlarla Soru-Cevap ve Geribildirim Toplantısı**: 19-23 Mayıs 2025
- **Final Tasarım Raporu Teslim Tarihi**: 13 Haziran 2025, 17:00
- **Final Yarışmaya Katılacak Takımların Açıklanması**: 11 Temmuz 2025
- **Final Yarışması**: Ağustos 2025, İTÜ Ayazağa Yerleşkesi
- **TEKNOFEST İstanbul**: Eylül 2025

## 📝 Lisans

MIT License

---

© 2025 High5 - TEKNOFEST 5G Konumlandırma Yarışması
