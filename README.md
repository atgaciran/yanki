# YANKI - Afet Yönetim ve Enkaz Analiz Sistemi

Bu proje, **Tulpar Advance-Up Hackathon** kapsamında geliştirilmiş fiziksel bir afet yönetim sistemidir.

YANKI, enkaz altındaki cihazlardan aldığı sensör verilerini (ısı, ses, hareket) işleyerek bir yaşam skoru hesaplar, operasyon merkezine anlık durum bildirir ve kurtarma ekipleri için en kısa rotayı oluşturur. Aynı zamanda afetzedeye yardım ekibinin yola çıktığına dair fiziksel geri bildirim (ışık ve ekran mesajı) sağlar.

## Hazırlayanlar

* **Muhammed Aksoy**
* **Tolga Seymen**
* **Yakup Karataş**

---

## Temel Özellikler

* **IoT Veri Takibi:** Arduino üzerinden sıcaklık, nem, ses ve hareket verilerinin anlık izlenmesi.
* **Akıllı Analiz:** Sensör verileri ve dış hava durumu API'sini kullanarak yaşam ihtimali hesaplanması.
* **Komuta Merkezi:** Streamlit tabanlı, operatör odaklı yönetim paneli.
* **Rota Planlama:** WKT formatındaki coğrafi verilerle en kısa müdahale rotasının çizilmesi.
* **Çift Yönlü İletişim:** Operatör onayı ile enkaz altındaki cihaza "Ekip Gönderildi" sinyalinin iletilmesi.

## Sistem Mimarisi

1.  **Donanım:** Arduino Uno, DHT11, PIR, Ses Sensörü, LCD Ekran.
2.  **Backend:** Python Flask (Veri işleme, API ve Veritabanı).
3.  **Frontend:** Streamlit (Harita, Analiz Kartları ve Yönetim Paneli).

---

## Kurulum

Projenin çalışması için gerekli tüm Python kütüphanelerini aşağıdaki komutla tek seferde kurabilirsiniz:

pip install flask flask-socketio pyserial tinydb requests streamlit pandas folium streamlit-folium simple-websocket osmnx networkx shapely

## Çalıştırma

Sistemi ayağa kaldırmak için aşağıdaki adımları sırasıyla uygulayın:

**1. Backend'i Başlatın:**
Veri akışını ve Arduino iletişimini sağlamak için terminalde:

python backend/app.py

**2. Arayüzü Başlatın:**
Komuta panelini açmak için yeni bir terminalde:

streamlit run frontend/dashboard.py
