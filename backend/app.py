import serial
import json
import requests
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from engine.depth_calc import calculate_depth 
from engine.analyzer import get_survival_score 
from database.db_manager import get_device_info, log_sensor_data
from datetime import datetime
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- ARDUINO VE PORT AYARLARI ---
# DİKKAT: Arduino IDE'de hangi portu görüyorsan onu yaz (Örn: COM3, COM5, /dev/ttyUSB0)
SERIAL_PORT = 'COM3' 
BAUD_RATE = 9600

try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    arduino.reset_input_buffer()
    print(f">>> {SERIAL_PORT} Portuna Başarıyla Bağlanıldı!")
except Exception as e:
    arduino = None
    print(f">>> HATA: Arduino Bağlanamadı! {e}")

# --- GLOBAL DEĞİŞKENLER (CACHE) ---
WEATHER_CACHE = {"sicaklik": -10.0, "durum": "Veri Bekleniyor", "last_update": 0}

# --- 1. HAVA DURUMU (CACHE) ---
def update_weather_cache(lat, lon):
    global WEATHER_CACHE
    if time.time() - WEATHER_CACHE["last_update"] < 900: return

    api_key = "172d155b07fea3bae213502b1ff4bdb5" 
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            WEATHER_CACHE["sicaklik"] = data['main']['temp']
            WEATHER_CACHE["durum"] = data['weather'][0]['description']
            WEATHER_CACHE["last_update"] = time.time()
            print(f">>> Hava Durumu Güncellendi: {WEATHER_CACHE['sicaklik']}C")
    except: pass

# --- 2. KURTARMA KOMUTU (EKİP GÖNDER - YEŞİL LED) ---
@app.route('/api/send-team', methods=['POST'])
def send_team():
    """Frontend 'EKİP GÖNDER' butonuna basılınca çalışır."""
    try:
        data = request.json
        target_id = data.get('id')
        print(f"\n>>> [OPERASYON] ID:{target_id} İÇİN EKİP GÖNDERİLİYOR...")
        
        if arduino:
            arduino.write(b"GREEN_ON\n") 
            print(">>> Arduino'ya 'GREEN_ON' komutu gönderildi.")
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Arduino yok"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 3. EKİBİ GERİ ÇEKME KOMUTU (YENİ EKLENDİ - RESET) ---
@app.route('/api/withdraw-team', methods=['POST'])
def withdraw_team():
    """Frontend 'EKİBİ GERİ ÇEK' butonuna basılınca çalışır."""
    try:
        data = request.json
        target_id = data.get('id')
        print(f"\n>>> [OPERASYON İPTAL] ID:{target_id} İÇİN EKİP GERİ ÇEKİLİYOR...")
        
        if arduino:
            # Burası Arduino'ya RESET komutunu gönderir
            arduino.write(b"RESET\n") 
            print(">>> Arduino'ya 'RESET' komutu gönderildi (Ölçüm Tekrar Başlıyor).")
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Arduino yok"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 4. SOCKET IO SİNYALİ (Alternatif) ---
@socketio.on('start_rescue')
def handle_rescue_start(json_data):
    if arduino:
        arduino.write(b"GREEN_ON\n")

# --- 5. VERİ İŞLEME DÖNGÜSÜ ---
def main_loop():
    print("--- YANKI AI Motoru Başlatıldı ---")
    while True:
        if arduino is None:
            time.sleep(1)
            continue

        try:
            if arduino.in_waiting > 0:
                try:
                    raw_line = arduino.readline().decode('utf-8', errors='ignore').strip()
                except: continue

                if not raw_line.startswith('{') or not raw_line.endswith('}'): continue
                
                try:
                    json_raw = json.loads(raw_line)
                except: continue

                # DB'den Cihaz bilgilerini al
                info = get_device_info(json_raw.get('id'))
                
                if info:
                    update_weather_cache(info['koordinat'][0], info['koordinat'][1])
                    
                    # Skor Hesapla
                    score = get_survival_score({
                        't': json_raw.get('sicaklik'), 
                        'h': json_raw.get('nem'), 
                        's': 1 if json_raw.get('ses') == "var" else 0, 
                        'm': 1 if json_raw.get('hareket') == "var" else 0, 
                        'r': -75,
                        'ext_t': WEATHER_CACHE["sicaklik"]
                    })

                    # Triyaj Rengi
                    color = "BLACK"
                    label = "BEKLEMEDE"
                    if score > 50: color, label = "RED", "ACİL"
                    elif score > 30: color, label = "YELLOW", "GÖZLEM"
                    elif score > 10: color, label = "GREEN", "STABİL"

                    depth = calculate_depth(-75)
                    zaman = datetime.now().strftime("%H:%M:%S")

                    final_packet = {
                        "id": info['id'],
                        "adres": info['adres'],
                        "sensor_verileri": {
                            "ic_sicaklik": f"{json_raw.get('sicaklik')}C",
                            "nem": f"%{json_raw.get('nem')}",
                            "vurus": "VAR" if json_raw.get('ses') == "var" else "YOK",
                            "hareket": "VAR" if json_raw.get('hareket') == "var" else "YOK"
                        },
                        "dis_ortam": {
                            "sicaklik": f"{WEATHER_CACHE['sicaklik']}C",
                            "durum": WEATHER_CACHE["durum"]
                        },
                        "analiz_destek": {
                            "yasam_ihtimali": f"%{score}",
                            "tahmini_derinlik": f"{depth}m",
                            "triyaj_rengi": color,
                            "durum": label,
                            "zaman": zaman
                        }
                    }

                    log_sensor_data(final_packet)
                    socketio.emit('new_signal', final_packet)
                    print(f"[{zaman}] ID:{json_raw.get('id')} | Skor: %{score} | {label}")
        
        except Exception as e:
            print(f"Hata: {e}")
            time.sleep(0.1)

if __name__ == '__main__':
    t = threading.Thread(target=main_loop, daemon=True)
    t.start()
    socketio.run(app, debug=True, port=5000, use_reloader=False, allow_unsafe_werkzeug=True)