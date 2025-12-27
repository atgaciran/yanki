import math
import joblib
import pandas as pd
import os

# Model dosya yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'yanki_ai_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')

def calculate_depth(rssi, environment='concrete'):
    """RSSI sinyal gücünden derinlik tahmini (Senin kodun)."""
    env_factors = {'air': 2.0, 'wood': 3.0, 'concrete': 4.0, 'dense_debris': 5.0}
    p0, n = -45, env_factors.get(environment, 3.5)
    
    if rssi >= p0: return 0.1
    try:
        distance = 10 ** ((p0 - rssi) / (10 * n))
        return round(distance, 2)
    except:
        return 0.0

def get_survival_score(data):
    """
    app.py ile tam uyumlu hibrit analiz motoru.
    data: {'t': temp, 'h': hum, 's': sound, 'm': move, 'r': rssi, 'ext_t': external_temp}
    """
    score = 0
    factors = []
    
    # 1. VERİLERİ AYIKLA (app.py'den gelen format)
    s_val = data.get('s', 0)     # 1 veya 0
    m_val = data.get('m', 0)     # 1 veya 0
    temp = data.get('t', 20.0)   # İç sıcaklık
    hum = data.get('h', 50.0)    # Nem
    rssi = data.get('r', -75.0)  # RSSI
    ext_t = data.get('ext_t', 15.0) # Dış hava durumu
    
    # --- 2. KURAL TABANLI MANTIK (Senin işlevli dediğin kısım) ---
    if s_val > 0:
        score += 45
        factors.append("Yüksek Ses/Vuruş")

    if m_val > 0:
        score += 30
        factors.append("Hareket Tespit Edildi")

    if 30 <= temp <= 38:
        score += 20
        factors.append("Normal Vücut Isısı")
    elif 25 <= temp < 30 or 38 < temp <= 42:
        score += 10
        factors.append("Riskli Vücut Isısı")

    if hum > 80:
        score += 5
        factors.append("Yüksek Nem (Nefes Belirtisi)")

    # ERZURUM / ETÜ ÖZEL ANALİZİ
    if ext_t < 0 and temp < 25:
        score += 15
        factors.append(f"KRİTİK: Erzurum Soğuğu ({ext_t}°C) Hipotermi Riski!")

    # --- 3. YAPAY ZEKA (AI) OPTİMİZASYONU ---
    final_score = score
    ai_status = False

    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            scaler = joblib.load(SCALER_PATH)
            
            # AI için girdi tablosu oluştur
            df = pd.DataFrame([[temp, hum, s_val, m_val, rssi, ext_t]], 
                             columns=['temp', 'hum', 'sound', 'move', 'rssi', 'ext_t'])
            
            scaled_input = scaler.transform(df)
            ai_prediction = model.predict(scaled_input)[0]
            
            # Hibrit Sonuç: Senin kuralların ve AI'nın tahmini ortalanır
            final_score = (score + ai_prediction) / 2
            ai_status = True
        except Exception as e:
            print(f"AI Analiz Hatası: {e}")

    final_score = min(100, round(final_score))
    
    # app.py sadece skoru beklediği için şimdilik int döndürüyoruz
    # Ancak daha fazla detay istersen bu yapıyı bir sözlük olarak da kullanabilirsin.
    return int(final_score)