import requests

def get_weather_data(lat, lon):
    api_key = "172d155b07fea3bae213502b1ff4bdb5" # Buraya kendi anahtarını yaz
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "dis_sicaklik": data['main']['temp'],
                "durum": data['weather'][0]['description'],
                "nem": data['main']['humidity']
            }
    except:
        return None # İnternet yoksa hata vermesin, sistemi durdurmasın