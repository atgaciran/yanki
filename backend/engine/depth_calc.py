import math

def calculate_depth(rssi):
    """
    Sinyal Sönümlenme Modeli (Log-Distance Path Loss Model)
    rssi: Sinyal gücü (dBm cinsinden, örn: -75)
    """
    # p0: 1 metredeki referans sinyal gücü (Standart -45 dBm)
    # n: Ortam yayılım sabiti (Enkaz/beton için 3.0 - 4.0 arası idealdir)
    p0 = -45 
    n = 3.5
    
    if rssi >= 0: return 0.5 # Hatalı veri koruması
    
    try:
        # Formül: d = 10^((p0 - rssi) / (10 * n))
        distance = 10 ** ((p0 - rssi) / (10 * n))
        return round(max(0.5, min(10.0, distance)), 2)
    except:
        return 2.0 # Hata durumunda güvenli varsayılan