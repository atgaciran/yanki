# BU DOSYA PROJENİN KONUM AYARLARINI TUTAR

# Erzurum / ETÜ Kampüs Civarı Merkezi (Harita buraya odaklanır)
MERKEZ_NOKTA = (39.919893, 41.238081)  # (Enlem, Boylam)

# --- KOORDİNAT SİSTEMİ (WKT FORMATI) ---
# DİKKAT: WKT Formatı şöyledir -> "POINT(BOYLAM ENLEM)"
# Yani Google Maps'teki (39.91..., 41.24...) sırasının TERSİDİR.
# Önce 41 (Doğu), Sonra 39 (Kuzey) yazılır.

LOCATIONS_WKT = {
    "AFAD": "POINT(41.244888 39.919612)", # Senin verdiğin ana konum 
    
    # --- YENİ EKLEYECEĞİN 4 BİNA ---
    # (Buradaki koordinatları Google Maps'ten alıp ters çevirerek yaz)
    
    1: "POINT(41.238412 39.919511)",      # Kütüphane
    2: "POINT(41.240826 39.918065)",      # Rektörlük
    3: "POINT(41.235428 39.916291)",      # Edebiyat Fakültesi
    4: "POINT(41.241428 39.922499)",      # YÜTAM
    5: "POINT(41.240187 39.919828)"       # Mühendislik Fakültesi
}

def get_bina_no(daire_id):
    """
    Cihaz ID'sine göre hangi binada olduğunu belirler.
    Eğer elinde çok cihaz varsa buradaki aralıkları genişletebilirsin.
    """
    try:
        d_id = int(daire_id)
        # Örnek Dağılım:
        if d_id == 1: return 5   # ID 1 -> Bina 5'te
        if 1 <= d_id <= 8: return 1
        if 9 <= d_id <= 16: return 2
        if 17 <= d_id <= 24: return 3
        if 25 <= d_id <= 32: return 4
        if 33 <= d_id <= 40: return 5
    except:
        return None
    return 1 # Varsayılan olarak Bina 1 döndür

BLOCKED_SEGMENTS = [
    {
        # Haritadaki göbeğin tam orta noktası (Tahmini koordinat, Google Maps'ten sağ tıkla alabilirsin)
        'merkez': (39.919075, 41.242080), 
        'yaricap': 20  # Göbeğin genişliğine göre 20-40 metre arası idealdir
    }
]