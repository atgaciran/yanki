def parse_serial_data(raw_line):
    """
    Arduino Formatı: ID:10,T:25.5,H:60,S:1,M:1,R:-75
    T: Sıcaklık, H: Nem, S: Ses, M: Hareket, R: RSSI
    """
    try:
        # Virgüllere göre ayır ve sözlük yapısına çevir
        parts = {p.split(':')[0]: p.split(':')[1] for p in raw_line.split(',')}
        return {
            "id": int(parts['ID']),
            "temp": float(parts['T']),
            "hum": float(parts['H']),
            "sound": int(parts['S']),
            "movement": int(parts['M']),
            "rssi": int(parts['R'])
        }
    except Exception as e:
        print(f"Ayrıştırma Hatası: {e}")
        return None