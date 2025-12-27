import streamlit as st
import pandas as pd
from tinydb import TinyDB, Query
import time
import os
import sys 
import folium
from streamlit_folium import st_folium
import requests 
import base64  # Resim okumak için şart

# --- 1. AYARLAR VE BAĞLANTILAR ---
st.set_page_config(
    page_title="YANKI AI | Komuta Merkezi", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend Yolu
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, '..', 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# Modüller
try:
    import shortest_path as sp
    from config import LOCATIONS_WKT 
except ImportError as e:
    st.error(f"Sistem Hatası: Backend modülleri eksik. {e}")
    st.stop()

# Veritabanı
DB_PATH = os.path.join(BACKEND_DIR, 'database', 'devices.json')
try:
    db = TinyDB(DB_PATH)
    logs_table = db.table('sensor_logs')
except Exception as e:
    st.error(f"Veritabanı Bağlantı Hatası: {DB_PATH}")
    st.stop()

# --- STATE YÖNETİMİ ---
if 'dispatched_ids' not in st.session_state:
    st.session_state['dispatched_ids'] = set()

if 'toast_message' not in st.session_state:
    st.session_state['toast_message'] = None

if 'secilen_hedef_bina' not in st.session_state:
    st.session_state['secilen_hedef_bina'] = None

if st.session_state['toast_message']:
    st.toast(st.session_state['toast_message'], icon="⚠️")
    st.session_state['toast_message'] = None

@st.cache_resource
def get_graph():
    return sp.harita_getir()

G = get_graph()

# --- 2. PROFESYONEL CSS TASARIMI VE GÖRSELLER ---
# Base64 dönüştürücü fonksiyon
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return None

# --- ARKA PLAN GÖRSELİ AYARI ---
bg_img_path = r"C:\Users\Tolga\Desktop\hackathon\frontend\assets\bg.png"
bg_img_base64 = get_base64_of_bin_file(bg_img_path)

if bg_img_base64:
    bg_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #ffffff;
    }}
    </style>
    """
else:
    bg_style = """<style>.stApp { background-color: #0d1117; color: #000000; }</style>"""

st.markdown(bg_style, unsafe_allow_html=True)

# --- DİĞER CSS KURALLARI ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    /* H1 başlık stili - Logo ve metni ortalamak için flex eklendi */
    h1 { 
        color: #000000; 
        font-family: 'Segoe UI', sans-serif; 
        font-weight: 600; 
        border-bottom: 1px solid #30363d; 
        padding-bottom: 15px; 
        margin-bottom: 30px; 
        letter-spacing: 1px;
        display: flex;           /* Logo ve metni yan yana getirmek için */
        align-items: center;     /* Dikeyde ortala */
        justify-content: center; /* Yatayda ortala */
    }
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); }

    /* GENEL KART YAPISI */
    .status-card {
        padding: 15px;
        margin-bottom: 0px; /* Butonla birleşmesi için */
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    /* KIRMIZI KART (ACİL) - Altı Düz (Buton Gelecek) */
    .card-red {
        background: linear-gradient(180deg, #3a0d0d 0%, #1a0505 100%);
        border-left: 4px solid #da3633;
        border-bottom: none; 
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
    }
    
    /* SARI KART (RİSKLİ) - Altı Yuvarlak (Buton Yok) */
    .card-yellow {
        background: linear-gradient(180deg, #3a2e05 0%, #1a1501 100%);
        border-left: 4px solid #d29922;
        border-radius: 6px; /* Tam yuvarlak */
        margin-bottom: 15px; /* Bir sonraki kartla mesafe */
    }

    .metric-label { font-size: 0.75rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: #f0f6fc; }
    .weather-widget { background-color: #0d1117; color: #58a6ff; padding: 12px; border-radius: 6px; border: 1px solid #1f6feb; text-align: center; font-weight: 600; margin-bottom: 20px; font-family: monospace; }
    h3 { color: #e6edf3; font-size: 1.3rem !important; margin-top: 0 !important; }

    /* BUTON ENTEGRASYONU */
    div.stButton > button {
        width: 100%;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
        margin-top: 0px;
        border-top: none;
        height: 45px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    /* Normal Buton (Gönder) */
    div.stButton > button {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid rgba(255,255,255,0.05);
    }
    div.stButton > button:hover {
        background-color: #30363d;
        color: white;
        border-color: #8b949e;
    }

    /* Geri Çek Butonu (Kırmızı) */
    button[kind="primary"] { 
        background-color: #da3633 !important; 
        color: white !important; 
        border: 1px solid #da3633 !important; 
    }
    button[kind="primary"]:hover { 
        background-color: #b31d1a !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- BAŞLIK (LOGO ENTEGRASYONU) ---
logo_img_path = r"C:\Users\Tolga\Desktop\hackathon\frontend\assets\logo.png"
logo_base64 = get_base64_of_bin_file(logo_img_path)

if logo_base64:
    # Logo varsa: Resim + Metin
    # height: 60px; logonun yüksekliğini ayarlar, isteğine göre değiştir.
    # margin-right: 15px; logo ile yazı arasındaki boşluk.
    header_html = f"""
    <h1>
        <img src="data:image/png;base64,{logo_base64}" style="height: 120px; margin-right: -5px; margin-top: -6px;">
        Afet Yönetim Sistemi
    </h1>
    """
else:
    # Logo bulunamazsa sadece metin (YANKI olmadan)
    st.markdown(
    "<h1 style='color:black'>Afet Yönetim Sistemi</h1>",
    unsafe_allow_html=True
)

st.markdown(header_html, unsafe_allow_html=True)


col_left, col_right = st.columns([2, 1.2])

# --- 3. VERİ HAZIRLIĞI ---
log_data = logs_table.all()
df_display = pd.DataFrame()

if log_data:
    df = pd.DataFrame(log_data)
    if not df.empty and 'id' in df.columns:
        df_latest = df.drop_duplicates(subset=['id'], keep='last')
        processed_rows = []
        for _, row in df_latest.iterrows():
            try:
                analiz = row.get('analiz_destek', {})
                sensor = row.get('sensor_verileri', {})
                dis_ortam = row.get('dis_ortam', {})
                try:
                    from config import get_bina_no
                    bina_numarasi = get_bina_no(row.get('id'))
                except:
                    bina_numarasi = 1

                processed_rows.append({
                    'id': row.get('id'),
                    'bina_no': bina_numarasi,
                    'renk': analiz.get('triyaj_rengi', 'BLACK'),
                    'durum_etiketi': analiz.get('durum', 'BILINMIYOR'),
                    'yasam_puani': analiz.get('yasam_ihtimali', '%0'),
                    'derinlik': analiz.get('tahmini_derinlik', '0m'),
                    'ic_isi': sensor.get('ic_sicaklik', 'N/A'),
                    'ses': sensor.get('vurus', 'YOK'),
                    'hareket': sensor.get('hareket', 'YOK'),
                    'dis_isi': dis_ortam.get('sicaklik', 'N/A'),
                    'dis_durum': dis_ortam.get('durum', '')
                })
            except Exception:
                continue
        df_display = pd.DataFrame(processed_rows)

# =================================================================================
# KUTUCUK 1: OPERASYON SAHASI (SOL)
# =================================================================================
with col_left:
    with st.container(border=True):
        st.subheader("OPERASYON SAHASI")
        ana_yol_kapali = False
        merkez_coords = sp.get_coords_from_wkt(LOCATIONS_WKT["AFAD"])
        m = folium.Map(location=merkez_coords, zoom_start=16, tiles='CartoDB positron')

        folium.Marker(merkez_coords, popup="KOMUTA MERKEZİ", icon=folium.Icon(color="blue", icon="home", prefix='fa')).add_to(m)

        bina_ids = [k for k in LOCATIONS_WKT.keys() if isinstance(k, int)]
        for i in bina_ids:
            coord = sp.get_coords_from_wkt(LOCATIONS_WKT[i])
            icon_color = "red" if st.session_state.get('secilen_hedef_bina') == i else "green"
            folium.Marker(coord, tooltip=f"Bina {i}", icon=folium.Icon(color=icon_color, icon="building", prefix='fa')).add_to(m)
            
        if st.session_state.get('secilen_hedef_bina'):
            hedef = st.session_state['secilen_hedef_bina']
            route_coords = sp.rota_hesapla(G, LOCATIONS_WKT["AFAD"], hedef, ana_yol_kapali)
            if route_coords:
                folium.PolyLine(route_coords, color="#f85149" if ana_yol_kapali else "#2f81f7", weight=4, opacity=0.9).add_to(m)
            else:
                st.error("Ulaşım Sağlanamıyor - Rota Yok")

        st_folium(m, width="100%", height=600)

# =================================================================================
# KUTUCUK 2: ANALİZ VE VERİLER (SAĞ)
# =================================================================================
with col_right:
    with st.container(border=True):
        st.subheader("ANALİZ SONUÇLARI")
        
        if not df_display.empty:
            son_dis_sicaklik = df_display.iloc[-1]['dis_isi']
            st.markdown(f"""<div class="weather-widget">DIŞ ORTAM SICAKLIĞI (API): {son_dis_sicaklik}</div>""", unsafe_allow_html=True)

            df_red = df_display[df_display['renk'] == 'RED']
            df_yellow = df_display[df_display['renk'] == 'YELLOW']

            tab1, tab2 = st.tabs(["ACİL DURUM", "RİSKLİ"])
            
            # --- ANA KART OLUŞTURUCU ---
            def create_card_with_button(row, card_type, enable_button=False):
                # HTML Kart Basımı (Üst Kısım)
                st.markdown(f"""
                    <div class="status-card {card_type}">
                        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                            <span style="font-weight:bold; font-size:1.1rem;">BİNA {row['bina_no']}</span>
                            <span style="background:rgba(0,0,0,0.3); padding:2px 6px; border-radius:4px; font-size:0.8rem;">ID: {row['id']}</span>
                        </div>
                        <div style="margin-bottom:10px; font-size:0.9rem;">
                            Durum: <strong>{row['durum_etiketi']}</strong> | Yaşam İhtimali: <strong>{row['yasam_puani']}</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; background:rgba(0,0,0,0.2); padding:8px; border-radius:4px;">
                            <div style="text-align:center;">
                                <div class="metric-label">SES</div><div class="metric-value">{row['ses']}</div>
                            </div>
                            <div style="text-align:center;">
                                <div class="metric-label">İÇ ISI</div><div class="metric-value">{row['ic_isi']}</div>
                            </div>
                            <div style="text-align:center;">
                                <div class="metric-label">DIŞ ISI</div><div class="metric-value">{row['dis_isi']}</div>
                            </div>
                        </div>
                         <div style="font-size:0.9rem; margin-top:5px; text-align:right;">Hareket: <b>{row['hareket']}</b></div>
                    </div>
                """, unsafe_allow_html=True)

                # --- BUTON KISMI (ALT KISIM) ---
                # Buton, HTML'den hemen sonra render edilir ve CSS ile birleşik görünür
                if enable_button:
                    is_dispatched = row['id'] in st.session_state['dispatched_ids']

                    if is_dispatched:
                        # GERİ ÇEK BUTONU (Kırmızı - Primary)
                        if st.button(f"EKİBİ GERİ ÇEK (Bina {row['bina_no']})", key=f"btn_withdraw_{row['id']}", type="primary"):
                            st.session_state['dispatched_ids'].remove(row['id'])
                            if st.session_state['secilen_hedef_bina'] == row['bina_no']:
                                st.session_state['secilen_hedef_bina'] = None 
                            st.session_state['toast_message'] = f"Ekipler Geri Çekildi: Bina {row['bina_no']}"
                            try:
                                requests.post("http://127.0.0.1:5000/api/withdraw-team", json={"id": int(row['id'])}, timeout=2)
                            except: pass 
                            st.rerun()
                    else:
                        # EKİP GÖNDER BUTONU (Normal)
                        if st.button(f"EKİP GÖNDER (Bina {row['bina_no']})", key=f"btn_send_{row['id']}"):
                            st.session_state['dispatched_ids'].add(row['id'])
                            st.session_state['secilen_hedef_bina'] = row['bina_no']
                            st.session_state['toast_message'] = f"Rota Belirlendi: Bina {row['bina_no']}"
                            try:
                                requests.post("http://127.0.0.1:5000/api/send-team", json={"id": int(row['id'])}, timeout=2)
                            except: pass
                            st.rerun()
                
                # Kartlar arası boşluk
                if enable_button:
                      st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)


            # --- SEKME 1: ACİL (KIRMIZI - BUTONLU) ---
            with tab1:
                if not df_red.empty:
                    for _, row in df_red.iterrows():
                        create_card_with_button(row, card_type="card-red", enable_button=True)
                else:
                    st.markdown("<div style='text-align:center; padding:20px; color:#555;'>Acil Durum Yok</div>", unsafe_allow_html=True)

            # --- SEKME 2: RİSKLİ (SARI - BUTONSUZ) ---
            with tab2:
                if not df_yellow.empty:
                    for _, row in df_yellow.iterrows():
                        create_card_with_button(row, card_type="card-yellow", enable_button=False)
                else:
                    st.markdown("<div style='text-align:center; padding:20px; color:#555;'>Riskli Durum Yok</div>", unsafe_allow_html=True)
        else:
            st.info("Sistem Beklemede: Veri Akışı Yok...")

# Otomatik Yenileme
time.sleep(1)
st.rerun()