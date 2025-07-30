# 🔥 HellTiger - Gelişmiş DDoS Test Aracı

<div align="center">

![HellTiger Logo](https://img.shields.io/badge/HellTiger-v2.0-red?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20Termux-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational%20Only-yellow?style=for-the-badge)

**Gelişmiş Askeri Sınıf DDoS Test ve Analiz Aracı**

</div>

---

## ⚠️ **ÖNEMLİ YASAL UYARI**

> **Bu araç yalnızca eğitim ve test amaçlı geliştirilmiştir. İzinsiz sistemlerde kullanımı KESİNLİKLE YASAKTIR!**
> 
> - ✅ Kendi sahip olduğunuz sistemlerde
> - ✅ Açık izin alınmış test ortamlarında  
> - ✅ Kontrollü eğitim laboratuvarlarında
> - ✅ Yasal penetrasyon testlerinde
> 
> **Bu aracın kötüye kullanımından tamamen KULLANICI SORUMLUDUR. Geliştiriciler hiçbir yasal yükümlülük kabul etmez.**

---

## 📋 **İçindekiler**

- [Özellikler](#-özellikler)
- [Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Platform Desteği](#-platform-desteği)
- [Örnekler](#-örnekler)
- [Sorun Giderme](#-sorun-giderme)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

---

## 🚀 **Özellikler**

### 🎯 **Temel Özellikler**
- **Çoklu Thread Desteği**: 1-1000 arası thread ile yüksek performans
- **Gerçek Zamanlı İzleme**: Anlık RPS, başarı oranı ve sistem kaynak monitörü
- **Akıllı HTTP Başlıkları**: Rastgele User-Agent ve gerçekçi HTTP başlıkları
- **Dinamik Yük Dağılımı**: Otomatik thread yönetimi ve yük dengeleme
- **Detaylı Raporlama**: Kapsamlı test sonucu analizi ve performans metrikleri

### 📊 **Gelişmiş Analiz**
- **Sistem Kaynak İzleme**: CPU, RAM ve GPU kullanım takibi
- **HTTP Durum Kodu Analizi**: Detaylı yanıt kodu istatistikleri
- **Hata Analizi**: Kategorize edilmiş hata raporları
- **Performans Skorlama**: Otomatik test performansı değerlendirmesi
- **Gerçek Zamanlı Grafikler**: Terminal tabanlı görsel göstergeler

### 🛡️ **Güvenlik ve Kontrol**
- **Etik Kullanım Kontrolü**: Zorunlu kullanım şartları onayı
- **Hedef Doğrulama**: URL format kontrolü ve güvenlik kontrolleri
- **Graceful Shutdown**: Ctrl+C ile güvenli test durdurma
- **Kaynak Koruması**: Sistem kaynak limitlerini aşmama kontrolü

---

## 💻 **Sistem Gereksinimleri**

### **Minimum Gereksinimler**
- **Python**: 3.7 veya üzeri
- **RAM**: 2 GB (önerilen: 4 GB+)
- **CPU**: 2 çekirdek (önerilen: 4+ çekirdek)
- **İnternet**: Stabil bağlantı

### **Önerilen Gereksinimler**
- **Python**: 3.9+
- **RAM**: 8 GB+
- **CPU**: 8+ çekirdek
- **GPU**: NVIDIA GPU (opsiyonel, performans izleme için)

---

## 🔧 **Kurulum**

### **1. Depoyu Klonlayın**
```bash
git clone https://github.com/kodclup-githup/helltiger.git
cd helltiger
```

### **2. Python Sanal Ortamı Oluşturun (Önerilen)**
```bash
# Linux/macOS
python3 -m venv helltiger-env
source helltiger-env/bin/activate

# Windows
python -m venv helltiger-env
helltiger-env\Scripts\activate
```

### **3. Gerekli Kütüphaneleri Yükleyin**
```bash
pip install -r requirements.txt
```

### **4. GPU Desteği (Opsiyonel)**
```bash
pip install GPUtil
```

---

## 🎮 **Kullanım**

### **Temel Kullanım**
```bash
python helltiger.py
```

### **Komut Satırı Parametreleri**
```bash
python helltiger.py --help
```

### **Etkileşimli Mod**
Program başlatıldığında size şu bilgileri soracaktır:

1. **🎯 Hedef Adres**: Test edilecek domain veya IP
2. **🔥 Thread Sayısı**: Eşzamanlı bağlantı sayısı (1-1000)
3. **⏱️ Test Süresi**: Test süresini saniye, dakika veya saat olarak
4. **⚡ Timeout**: İstek başına maksimum bekleme süresi

### **Örnek Kullanım Senaryoları**

#### **Hafif Test (Başlangıç)**
- **Thread**: 25
- **Süre**: 30 saniye
- **Timeout**: 5 saniye

#### **Normal Test**
- **Thread**: 50
- **Süre**: 2 dakika
- **Timeout**: 5 saniye

#### **Yoğun Test (Deneyimli Kullanıcılar)**
- **Thread**: 100+
- **Süre**: 5+ dakika
- **Timeout**: 3 saniye

---

## 🖥️ **Platform Desteği**

| Platform | Durum | Notlar |
|----------|-------|--------|
| **🐧 Linux** | ✅ Tam Destek | Tüm özellikler sorunsuz çalışır |
| **🪟 Windows** | ✅ Tam Destek | Tüm özellikler sorunsuz çalışır |
| **📱 Termux (Android)** | ✅ Desteklenir | PyDroid3'te çalışmaz, sadece Termux |
| **🍎 macOS** | ✅ Desteklenir | Test edilmiş, sorunsuz çalışır |

### **Platform Özel Kurulum Notları**

#### **🐧 Linux**
```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r requirements.txt
```

#### **🪟 Windows**
```cmd
# Python 3.7+ Microsoft Store'dan veya python.org'dan indirin
pip install -r requirements.txt
```

#### **📱 Termux (Android)**
```bash
pkg update && pkg upgrade
pkg install python
pip install -r requirements.txt
```

---

## 📊 **Örnekler**

### **Örnek 1: Yerel Test Sunucusu**
```
Hedef: localhost:8080
Thread: 25
Süre: 30 saniye
Timeout: 5 saniye
```

### **Örnek 2: Kendi Web Siteniz**
```
Hedef: https://kendi-siteniz.com
Thread: 50
Süre: 2 dakika
Timeout: 5 saniye
```

### **Örnek 3: Yük Testi**
```
Hedef: https://test-sunucunuz.com
Thread: 100
Süre: 5 dakika
Timeout: 3 saniye
```

---

## 📈 **Çıktı Açıklaması**

### **Gerçek Zamanlı İzleme**
- **📊 İlerleme**: Test tamamlanma yüzdesi
- **🚀 Anlık RPS**: Saniye başına istek sayısı
- **🎯 Toplam İstek**: Gönderilen toplam istek sayısı
- **✅ Başarı Oranı**: Başarılı isteklerin yüzdesi
- **📈 Ortalama Yanıt**: Ortalama yanıt süresi

### **Sistem Kaynak Monitörü**
- **🖥️ CPU**: İşlemci kullanım yüzdesi
- **🧠 RAM**: Bellek kullanım durumu
- **🎮 GPU**: Grafik kartı kullanımı (varsa)

### **Final Raporu**
- **📊 Performans Metrikleri**: Detaylı istatistikler
- **📋 HTTP Durum Kodları**: Yanıt kodu dağılımı
- **🚨 Hata Analizi**: Hata türleri ve sayıları
- **🏆 Performans Skoru**: Otomatik değerlendirme (0-100)

---

## 🔧 **Sorun Giderme**

### **Yaygın Sorunlar ve Çözümleri**

#### **❌ ModuleNotFoundError**
```bash
# Çözüm: Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

#### **❌ Permission Denied (Linux/macOS)**
```bash
# Çözüm: Python3 kullanın
python3 helltiger.py
```

#### **❌ GPU İzleme Çalışmıyor**
```bash
# Çözüm: GPUtil yükleyin (opsiyonel)
pip install GPUtil
```

#### **❌ Yüksek CPU Kullanımı**
- Thread sayısını azaltın (25-50 arası deneyin)
- Timeout süresini artırın
- Test süresini kısaltın

#### **❌ Düşük Performans**
- İnternet bağlantınızı kontrol edin
- Hedef sunucunun erişilebilir olduğundan emin olun
- Firewall/antivirus ayarlarını kontrol edin

---

## 🛡️ **Güvenlik Notları**

### **Etik Kullanım İlkeleri**
1. **Sadece kendi sistemlerinizde test yapın**
2. **İzin almadan başkasının sistemini test etmeyin**
3. **Yasal sınırlar içinde kalın**
4. **Test sonuçlarını sorumlu bir şekilde kullanın**

### **Yasal Sorumluluk**
- Bu araç eğitim amaçlıdır
- Kötüye kullanımdan kullanıcı sorumludur
- Geliştiriciler yasal yükümlülük kabul etmez
- Kullanım öncesi yasal danışmanlık alın

---

## 🤝 **Katkıda Bulunma**

### **Nasıl Katkıda Bulunabilirsiniz?**
1. **Fork** edin
2. **Feature branch** oluşturun (`git checkout -b feature/yeni-ozellik`)
3. **Commit** yapın (`git commit -am 'Yeni özellik eklendi'`)
4. **Push** edin (`git push origin feature/yeni-ozellik`)
5. **Pull Request** oluşturun

### **Katkı Alanları**
- 🐛 Bug düzeltmeleri
- ✨ Yeni özellikler
- 📚 Dokümantasyon iyileştirmeleri
- 🌍 Çeviri desteği
- 🧪 Test senaryoları

---

## 📞 **İletişim ve Destek**

### **Geliştirici**
- **👨‍💻 Geliştirici**: kodclub

### **Destek Kanalları**
- **🐛 Bug Raporu**: GitHub Issues
- **💡 Özellik İsteği**: GitHub Discussions
- **❓ Sorular**: GitHub Discussions

---

## 📄 **Lisans**

Bu proje **sadece eğitim amaçlı** geliştirilmiştir. 

### **Kullanım Şartları**
- ✅ Eğitim ve öğrenme amaçlı kullanım
- ✅ Kendi sistemlerinizde test
- ✅ Açık kaynak geliştirme
- ❌ Ticari kullanım
- ❌ Kötü niyetli kullanım
- ❌ İzinsiz sistem testleri

---

## 🏆 **Teşekkürler**

Bu projeyi geliştirirken kullanılan açık kaynak kütüphanelere ve topluluk katkılarına teşekkürler:

- **requests**: HTTP istekleri için
- **psutil**: Sistem kaynak izleme için
- **GPUtil**: GPU izleme için
- **threading**: Çoklu thread desteği için

---

<div align="center">

**🔥 HellTiger v2.0 - Güçlü, Güvenli, Eğitici 🔥**

*Sadece eğitim amaçlı - Sorumlu kullanın*

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)](https://python.org)
[![Educational Purpose](https://img.shields.io/badge/Purpose-Educational-green?style=for-the-badge)](https://github.com)

</div>