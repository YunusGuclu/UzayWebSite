# utils.py
import requests
from datetime import datetime
from .models import SpaceXLaunch, ISSLocation, SolarSystemBody, SpaceNews, PlanetMoon, DwarfPlanet, Asteroid,Astronaut
from django.utils import timezone

def fetch_spacex_launches():
    """SpaceX fırlatmalarını çek ve veritabanına kaydet"""
    url = "https://api.spacexdata.com/v4/launches/latest"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Eğer bu fırlatma zaten varsa güncelle, yoksa yeni oluştur
            launch, created = SpaceXLaunch.objects.get_or_create(
                mission_name=data['name'],
                defaults={
                    'launch_date': timezone.make_aware(datetime.strptime(data['date_utc'], "%Y-%m-%dT%H:%M:%S.%fZ")),
                    'rocket_name': data['rocket'],
                    'launch_success': data['success'],
                    'details': data.get('details', ''),
                    'mission_patch': data['links']['patch']['small'] if data['links'].get('patch') else None,
                    'video_link': data['links'].get('webcast')
                }
            )
            print("SpaceX verisi başarıyla kaydedildi")
            return launch
    except Exception as e:
        print(f"SpaceX API Hatası: {e}")
        return None

def fetch_iss_location():
    """ISS'in mevcut konumunu çek"""
    print("ISS konum verisi çekme işlemi başladı...")
    try:
        # ISS konum API'si
        iss_url = "http://api.open-notify.org/iss-now.json"
        
        # ISS konumunu al
        iss_response = requests.get(iss_url, timeout=5)
        iss_response.raise_for_status()
        iss_data = iss_response.json()
        
        try:
            # İnsan sayısını al (ayrı try-except bloğunda)
            people_url = "http://api.open-notify.org/astros.json"
            people_response = requests.get(people_url, timeout=5)
            people_response.raise_for_status()
            people_data = people_response.json()
            people_count = people_data.get('number', 0)
        except Exception as e:
            print(f"İnsan sayısı çekme hatası: {str(e)}")
            people_count = 0  # Hata durumunda varsayılan değer
        
        # Yeni konum oluştur
        location = ISSLocation.objects.create(
            latitude=float(iss_data['iss_position']['latitude']),
            longitude=float(iss_data['iss_position']['longitude']),
            people_in_space=people_count,
            timestamp=timezone.now()
        )
        
        print(f"ISS konumu güncellendi: Lat={location.latitude}, Long={location.longitude}, İnsan={location.people_in_space}")
        return location
            
    except Exception as e:
        print(f"ISS veri çekme hatası: {str(e)}")
        
        # Hata durumunda son başarılı konumu döndür
        try:
            last_location = ISSLocation.objects.latest('timestamp')
            print("Son başarılı konum kullanılıyor")
            return last_location
        except:
            return None
    
def fetch_solar_system_data():
    """Güneş sistemi verilerini çek ve veritabanına kaydet"""
    url = "https://api.le-systeme-solaire.net/rest/bodies/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['bodies']
            planets_added = 0
            
            for body in data:
                if body['isPlanet']:  # Sadece gezegenleri al
                    planet, created = SolarSystemBody.objects.get_or_create(
                        name=body['name'],
                        defaults={
                            'english_name': body['englishName'],
                            'body_type': 'Planet',
                            'mass': body.get('mass', {}).get('massValue'),
                            'gravity': body.get('gravity'),
                            'mean_radius': body.get('meanRadius'),
                            'moons_count': len(body.get('moons', []) or [])
                        }
                    )
                    if created:
                        planets_added += 1
            
            print(f"{planets_added} yeni gezegen kaydedildi")
            return SolarSystemBody.objects.filter(body_type='Planet')
    except Exception as e:
        print(f"Güneş Sistemi API Hatası: {e}")
        return None

def safe_get(data, key, default=None):
    """Güvenli bir şekilde sözlükten veri çeker"""
    try:
        if isinstance(data, dict):
            value = data.get(key, default)
            return value if value is not None else default
        return default
    except:
        return default
    
def fetch_space_news():
    """Uzay haberlerini çek ve veritabanına kaydet (maksimum 30 haber)"""
    url = "https://api.spaceflightnewsapi.net/v4/articles?limit=30"
    try:
        response = requests.get(url)
        print(f"API Yanıt Kodu: {response.status_code}")
        
        if response.status_code == 200:
            articles = response.json()['results']
            
            # Önce eski haberleri sil
            SpaceNews.objects.all().delete()
            news_added = 0
            
            # Yeni haberleri ekle
            for article in articles:
                try:
                    news = SpaceNews.objects.create(
                        title=article['title'],
                        summary=article['summary'],
                        published_date=timezone.make_aware(datetime.strptime(article['published_at'], "%Y-%m-%dT%H:%M:%SZ")),
                        news_url=article['url'],
                        image_url=article['image_url']
                    )
                    news_added += 1
                    print(f"Yeni haber eklendi: {article['title']}")
                except Exception as e:
                    print(f"Haber kaydedilirken hata: {str(e)}")
                    continue
            
            print(f"Toplam {news_added} yeni haber eklendi.")
            return SpaceNews.objects.all().order_by('-published_date')
    except Exception as e:
        print(f"Haber API Hatası: {str(e)}")
        return None

    
def clean_old_data():
    """Eski verileri temizle"""
    try:
        # 7 günden eski ISS konumlarını sil
        old_date = timezone.now() - timezone.timedelta(days=7)
        deleted_count = ISSLocation.objects.filter(timestamp__lt=old_date).delete()
        print(f"{deleted_count[0]} eski ISS konumu silindi")
        
        # 30 günden eski haberleri sil
        old_news_date = timezone.now() - timezone.timedelta(days=30)
        deleted_news = SpaceNews.objects.filter(published_date__lt=old_news_date).delete()
        print(f"{deleted_news[0]} eski haber silindi")
    except Exception as e:
        print(f"Veri temizleme hatası: {e}")

# utils.py'a eklenecek fetch fonksiyonları

def fetch_planet_moons():
    """Gezegenlerin uydularını çek"""
    print("Uydu verisi çekme işlemi başladı...")
    url = "https://api.le-systeme-solaire.net/rest/bodies/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bodies = response.json()['bodies']
            moons_added = 0
            
            for body in bodies:
                if body.get('aroundPlanet') and not body.get('isPlanet', False):
                    try:
                        moon, created = PlanetMoon.objects.get_or_create(
                            name=body['name'],
                            defaults={
                                'planet_name': safe_get(body.get('aroundPlanet', {}), 'planet', ''),
                                'discovery_date': safe_get(body, 'discoveryDate', ''),
                                'discovered_by': safe_get(body, 'discoveredBy', ''),
                                'mass': safe_get(body.get('mass', {}), 'massValue', 0),
                                'radius': safe_get(body, 'meanRadius', 0),
                                'density': safe_get(body, 'density', 0),
                                'gravity': safe_get(body, 'gravity', 0)
                            }
                        )
                        if created:
                            moons_added += 1
                            print(f"Yeni uydu eklendi: {body['name']}")
                    except Exception as e:
                        print(f"Uydu kaydedilirken hata: {body['name']} - {str(e)}")
            
            print(f"Toplam {moons_added} yeni uydu eklendi.")
            return PlanetMoon.objects.count()
    except Exception as e:
        print(f"Moon API Hatası: {str(e)}")
        return None


# Cüce gezegen resim URL'leri sözlüğü - her gezegen için özel resim
DWARF_PLANET_IMAGES = {
    "Pluto": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Pluto_in_True_Color_-_High-Res.jpg",
    "Ceres": "https://upload.wikimedia.org/wikipedia/commons/7/76/Ceres_-_RC3_-_Haulani_Crater_%2822381131691%29.jpg",
    "Eris": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Eris_and_dysnomia.jpg",
    "Haumea": "https://upload.wikimedia.org/wikipedia/commons/9/95/Haumea_%282018%29.jpg",
    "Makemake": "https://upload.wikimedia.org/wikipedia/commons/2/25/Makemake_art.png",
}

def fetch_dwarf_planets():
    """Cüce gezegen verilerini çek"""
    print("Cüce gezegen verisi çekme işlemi başladı...")
    url = "https://api.le-systeme-solaire.net/rest/bodies/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bodies = response.json()['bodies']
            dwarfs_added = 0
            
            for body in bodies:
                if body.get('isPlanet') == False and body.get('bodyType', '').lower() == 'dwarf planet':
                    try:
                        # Cüce gezegen için resmi al
                        image_url = DWARF_PLANET_IMAGES.get(body['englishName'])
                        
                        # Eğer resim bulunamadıysa varsayılan resmi kullan
                        if not image_url:
                            print(f"Uyarı: {body['englishName']} için resim bulunamadı, varsayılan resim kullanılıyor.")
                            image_url = "https://upload.wikimedia.org/wikipedia/commons/e/ef/Pluto_in_True_Color_-_High-Res.jpg"
                        
                        dwarf, created = DwarfPlanet.objects.get_or_create(
                            name=body['name'],
                            defaults={
                                'english_name': body['englishName'],
                                'mass': safe_get(body.get('mass', {}), 'massValue', 0),
                                'radius': safe_get(body, 'meanRadius', 0),
                                'density': safe_get(body, 'density', 0),
                                'gravity': safe_get(body, 'gravity', 0),
                                'escape_velocity': safe_get(body, 'escape', 0),
                                'mean_temperature': safe_get(body, 'meanTemperature', 0),
                                'moons_count': len(body.get('moons', []) or []),
                                'discovery_date': safe_get(body, 'discoveryDate', ''),
                                'discovered_by': safe_get(body, 'discoveredBy', ''),
                                'image_url': image_url
                            }
                        )
                        
                        if not created:  # Eğer kayıt zaten varsa, resmi güncelle
                            dwarf.image_url = image_url
                            dwarf.save()
                            
                        if created:
                            dwarfs_added += 1
                            print(f"Yeni cüce gezegen eklendi: {body['name']}")
                    except Exception as e:
                        print(f"Cüce gezegen kaydedilirken hata: {body['name']} - {str(e)}")
            
            print(f"Toplam {dwarfs_added} yeni cüce gezegen eklendi.")
            return DwarfPlanet.objects.count()
    except Exception as e:
        print(f"Dwarf Planet API Hatası: {str(e)}")
        return None
    
def fetch_asteroids():
    """Le Systeme Solaire API'den asteroid verilerini çek"""
    print("Asteroid verisi çekme işlemi başladı...")
    url = "https://api.le-systeme-solaire.net/rest/bodies/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bodies = response.json()['bodies']
            asteroids_added = 0
            
            for body in bodies:
                if body.get('bodyType', '').lower() == 'asteroid':
                    try:
                        asteroid, created = Asteroid.objects.get_or_create(
                            name=body['name'],
                            defaults={
                                'designation': safe_get(body, 'id', ''),
                                'body_type': 'Asteroid',
                                'mass': safe_get(body.get('mass', {}), 'massValue', 0),
                                'diameter': safe_get(body, 'meanRadius', 0) * 2 if safe_get(body, 'meanRadius') else None,
                                'density': safe_get(body, 'density', 0),
                                'gravity': safe_get(body, 'gravity', 0),
                                'orbit_period': safe_get(body, 'sideralOrbit', 0),
                                'is_potentially_hazardous': False
                            }
                        )
                        
                        if created:
                            asteroids_added += 1
                            print(f"Yeni asteroid eklendi: {body['name']}")
                            
                    except Exception as e:
                        print(f"Asteroid kaydedilirken hata ({body['name']}): {str(e)}")
                        continue
            
            print(f"Toplam {asteroids_added} yeni asteroid eklendi.")
            return Asteroid.objects.count()
            
    except Exception as e:
        print(f"Asteroid API Hatası: {str(e)}")
        return None
    

def fetch_astronauts():
    try:
        nasa_response = requests.get("http://api.open-notify.org/astros.json")
        nasa_data = nasa_response.json()
        current_astronauts = []
        
        # Astronot bilgileri sözlüğü
        astronaut_info = {
            # NASA Astronotları
            "Jasmin Moghbeli": {
                "agency": "NASA",
                "role": "Commander",
                "image": "https://www.nasa.gov/sites/default/files/thumbnails/image/jsc2021e010805.jpg"
            },
            "Loral O'Hara": {
                "agency": "NASA",
                "role": "Flight Engineer",
                "image": "https://www.nasa.gov/sites/default/files/thumbnails/image/jsc2018e091162.jpg"
            },
            
            # ESA Astronotları
            "Andreas Mogensen": {
                "agency": "ESA",
                "role": "Flight Engineer",
                "image": "https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2023/08/andreas_mogensen_official_portrait_2023/25028514-1-eng-GB/Andreas_Mogensen_official_portrait_2023_pillars.jpg"
            },
            
            # JAXA Astronotları
            "Satoshi Furukawa": {
                "agency": "JAXA",
                "role": "Flight Engineer",
                "image": "https://iss.jaxa.jp/en/astro/biographies/furukawa/images/furukawa_01.jpg"
            },
            
            # Roscosmos Astronotları
            "Oleg Kononenko": {
                "agency": "Roscosmos",
                "role": "Commander",
                "image": "https://www.roscosmos.ru/media/img/2023/Aug/kononenkook.jpg"
            },
            "Nikolai Chub": {
                "agency": "Roscosmos",
                "role": "Flight Engineer",
                "image": "https://www.roscosmos.ru/media/img/2023/Aug/chubna.jpg"
            },
            "Konstantin Borisov": {
                "agency": "Roscosmos",
                "role": "Flight Engineer",
                "image": "https://www.roscosmos.ru/media/img/2023/Aug/borisovkd.jpg"
            }
        }

        for person in nasa_data['people']:
            name = person['name']
            spacecraft = person['craft']
            
            # Varsayılan değerler
            default_info = {
                "agency": "NASA",
                "role": "Flight Engineer",
                "image": "https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png"
            }
            
            # Astronot bilgilerini al veya varsayılan değerleri kullan
            info = astronaut_info.get(name, default_info)
            
            # Ajans belirleme mantığı
            if "Shenzhou" in spacecraft:
                info["agency"] = "CNSA"
            elif any(russian in name for russian in ["Kononenko", "Chub", "Borisov", "Prokopyev", "Petelin"]):
                info["agency"] = "Roscosmos"
            
            # Astronot modelini güncelle veya oluştur
            astronaut, created = Astronaut.objects.get_or_create(
                name=name,
                defaults={
                    'spacecraft': spacecraft,
                    'role': info["role"],
                    'status': 'active',
                    'agency': info["agency"],
                    'image_url': info["image"]
                }
            )

            if not created:
                astronaut.spacecraft = spacecraft
                astronaut.status = 'active'
                astronaut.agency = info["agency"]
                astronaut.role = info["role"]
                astronaut.image_url = info["image"]
                astronaut.save()

            current_astronauts.append(astronaut)
            print(f"Astronot güncellendi: {name} - {info['agency']}")

        # İnaktif astronotları güncelle
        Astronaut.objects.exclude(name__in=[a.name for a in current_astronauts]).update(status='inactive')

        return True

    except Exception as e:
        print(f"Astronot verisi çekilirken hata oluştu: {e}")
        return False