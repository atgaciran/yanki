import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os

def train_ai():
    # Klasör Kontrolü
    current_dir = os.path.dirname(os.path.abspath(__file__))
    engine_dir = os.path.join(current_dir, 'engine')
    if not os.path.exists(engine_dir): os.makedirs(engine_dir)

    # 1. VERİ SETİ OLUŞTURMA
    data = []
    for _ in range(5000):
        t = np.random.uniform(15, 40)
        h = np.random.uniform(30, 95)
        s = np.random.randint(0, 2)
        m = np.random.randint(0, 2)
        r = np.random.uniform(-100, -40)
        ext_t = np.random.uniform(-15, 35)
        
        # Matematiksel Mantık (Model bunu öğrenecek)
        score = (s * 40) + (m * 20) + (h * 0.1)
        if t < 25: score += 10
        if ext_t < 5 and t < 22: score += 25
        score = min(100, max(0, score))
        data.append([t, h, s, m, r, ext_t, score])

    df = pd.DataFrame(data, columns=['temp', 'hum', 'sound', 'move', 'rssi', 'ext_t', 'score'])

    # 2. DOĞRULUK ARTIRICI KATMAN (Scaling)
    X = df.drop('score', axis=1)
    y = df['score']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X) # Sensör verilerini standardize eder

    # Veriyi böl
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

    # 3. EĞİTİM
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 4. SONUÇLARI GÖSTER
    preds = model.predict(X_test)
    print("\n--- EĞİTİM SONUÇLARI ---")
    print(f"BAŞARI YÜZDESİ (R2): %{round(r2_score(y_test, preds)*100, 2)}")
    print(f"HATA PAYI (MAE): {round(mean_absolute_error(y_test, preds), 2)} puan")

    # 5. KAYDET
    joblib.dump(model, os.path.join(engine_dir, 'yanki_ai_model.pkl'))
    joblib.dump(scaler, os.path.join(engine_dir, 'scaler.pkl')) # Scaler'ı da kaydetmeliyiz!
    print("\nModel ve Ölçekleyici başarıyla kaydedildi.")

if __name__ == "__main__":
    train_ai()