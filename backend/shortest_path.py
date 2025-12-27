import osmnx as ox
import networkx as nx
from shapely import wkt
from shapely.geometry import Point

# --- CONFIG DOSYASINDAN VERİLERİ ÇEK ---
try:
    from config import MERKEZ_NOKTA, LOCATIONS_WKT, get_bina_no, BLOCKED_SEGMENTS
except ImportError:
    print("HATA: config.py dosyası bulunamadı veya veriler eksik!")
    MERKEZ_NOKTA = (39.919893, 41.238081)
    LOCATIONS_WKT = {}
    BLOCKED_SEGMENTS = []

def get_coords_from_wkt(wkt_string):
    """
    WKT stringini ('POINT(x y)') okur ve (Lat, Lon) tuple'ına çevirir.
    """
    if not wkt_string: return (0, 0)
    try:
        point = wkt.loads(wkt_string)
        return (float(point.y), float(point.x)) # Garanti olsun diye float'a çeviriyoruz
    except Exception as e:
        print(f"WKT Parse Hatası: {e}")
        return (0,0)

def harita_getir():
    print(f"Harita hazırlanıyor... Merkez: {MERKEZ_NOKTA}")
    # dist=2000 metre yarıçapında Erzurum haritasını indirir
    G = ox.graph_from_point(MERKEZ_NOKTA, dist=2000, network_type='drive')
    return G

def rota_hesapla(G, baslangic_wkt, hedef_bina_id, ana_yol_kapali=False):
    # 1. Config'den hedefi al
    hedef_wkt = LOCATIONS_WKT.get(hedef_bina_id)
    
    if not hedef_wkt or not baslangic_wkt:
        return None
    
    # 2. Koordinata çevir
    baslangic_coords = get_coords_from_wkt(baslangic_wkt) # (Lat, Lon)
    hedef_coords = get_coords_from_wkt(hedef_wkt)         # (Lat, Lon)
    
    # Grafiğin kopyasını al (Orijinal harita bozulmasın diye)
    G_temp = G.copy()
    
    # --- YENİ BÖLÜM: BELİRLİ KOORDİNATLAR ARASINI KAPATMA ---
    if BLOCKED_SEGMENTS:
        # print(f"Simülasyon: {len(BLOCKED_SEGMENTS)} adet yol kapatılıyor...")
        for p1, p2 in BLOCKED_SEGMENTS:
            try:
                # DÜZELTME BURADA YAPILDI: Koordinatları float() içine aldık.
                # p1[1]=Boylam (Longitude), p1[0]=Enlem (Latitude)
                u = ox.distance.nearest_nodes(G_temp, float(p1[1]), float(p1[0])) 
                v = ox.distance.nearest_nodes(G_temp, float(p2[1]), float(p2[0]))
                
                # Gidiş Yönü (u -> v)
                if G_temp.has_edge(u, v):
                    for key in G_temp[u][v]:
                        G_temp[u][v][key]['length'] = 999999999 
                
                # Dönüş Yönü (v -> u)
                if G_temp.has_edge(v, u):
                    for key in G_temp[v][u]:
                        G_temp[v][u][key]['length'] = 999999999
            except Exception as e:
                print(f"Bloklama Hatası: {e}")
                continue

    # --- ESKİ SİMÜLASYON: TÜM ANA YOLLARI KAPAT ---
    if ana_yol_kapali:
        for u, v, k, data in G_temp.edges(keys=True, data=True):
            way_type = str(data.get('highway', ''))
            if 'primary' in way_type or 'secondary' in way_type or 'trunk' in way_type:
                data['length'] = data['length'] * 50000

    # En yakın yol düğümlerini bul (Başlangıç ve Bitiş için)
    # Burada da float dönüşümü ile garantiye alıyoruz
    try:
        orig_node = ox.distance.nearest_nodes(G_temp, float(baslangic_coords[1]), float(baslangic_coords[0]))
        dest_node = ox.distance.nearest_nodes(G_temp, float(hedef_coords[1]), float(hedef_coords[0]))

        # Rota hesapla
        route_nodes = nx.shortest_path(G_temp, orig_node, dest_node, weight='length')
        
        # Koordinat listesi oluştur
        route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route_nodes]
        
        # Çizgiyi tam noktalara bağla
        full_path = [baslangic_coords] + route_coords + [hedef_coords]
        
        return full_path
    
    except nx.NetworkXNoPath:
        print("Hata: Yol bulunamadı!")
        return None
    except Exception as e:
        print(f"Rota Hesaplama Hatası: {e}")
        return None