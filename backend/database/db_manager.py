from tinydb import TinyDB, Query

# Veritabanı dosyasını bağla
db = TinyDB('backend/database/devices.json')

# Tabloları ayırıyoruz: 
# 'devices' tablosu sabit bina bilgilerini tutar.
# 'sensor_logs' tablosu gelen anlık verileri tarihçesiyle tutar.
devices_table = db.table('_default') # Varsayılan tablo (Bina bilgileri)
logs_table = db.table('sensor_logs')  # Yeni tablo (Dinamik kayıtlar)

def get_device_info(device_id):
    """Cihaz ID'sine göre bina adres ve koordinat bilgilerini getirir."""
    Device = Query()
    # device_id'nin integer olduğundan emin olarak arama yapıyoruz
    result = devices_table.search(Device.id == int(device_id))
    return result[0] if result else None

def log_sensor_data(data_packet):
    """
    Gelen her yeni veriyi zaman damgasıyla birlikte 
    'sensor_logs' tablosuna dinamik olarak ekler.
    """
    try:
        logs_table.insert(data_packet)
        return True
    except Exception as e:
        print(f"Veritabanı Yazma Hatası: {e}")
        return False

def update_device_status(device_id, status):
    """Cihazın genel durumunu (Aktif/Pasif/Kurtarıldı) günceller."""
    Device = Query()
    devices_table.update({'status': status}, Device.id == int(device_id))