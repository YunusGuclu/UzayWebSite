# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import SpaceXLaunch, ISSLocation, SolarSystemBody, SpaceNews,PlanetMoon,DwarfPlanet,Asteroid,Astronaut
from .utils import fetch_spacex_launches, fetch_iss_location, fetch_solar_system_data, fetch_space_news,fetch_astronauts,fetch_planet_moons,fetch_dwarf_planets,fetch_asteroids,fetch_dwarf_planets,fetch_planet_moons,fetch_asteroids


def home(request):
    try:
        # ISS verilerini çek
        iss_data = fetch_iss_location()
        
        # SpaceX fırlatması
        try:
            latest_launch = SpaceXLaunch.objects.latest('launch_date')
        except SpaceXLaunch.DoesNotExist:
            latest_launch = None
        
        # Gezegenler ve haberler
        planets = SolarSystemBody.objects.filter(body_type='Planet')
        latest_news = SpaceNews.objects.all().order_by('-published_date')[:3]

        context = {
            'latest_launch': latest_launch,
            'iss_location': iss_data,  # Güncel ISS verisi
            'planets': planets,
            'latest_news': latest_news,
        }
        return render(request, 'home.html', context)
        
    except Exception as e:
        print(f"Ana sayfa yükleme hatası: {str(e)}")
        return render(request, 'home.html', {'error': 'Veriler yüklenirken bir hata oluştu'})

def news(request):
    try:
        # Haberleri güncelle
        fetch_space_news()
        # Tüm haberleri getir
        news_list = SpaceNews.objects.all().order_by('-published_date')
        print(f"Toplam {news_list.count()} haber bulundu")  # Debug için
        return render(request, 'news.html', {'news_list': news_list})
    except Exception as e:
        print(f"Haber görüntüleme hatası: {e}")
        return render(request, 'news.html', {'news_list': []})

def launches(request):
    launches = SpaceXLaunch.objects.all().order_by('-launch_date')
    return render(request, 'launches.html', {'launches': launches})

def iss_tracker(request):
    """ISS takip sayfası"""
    try:
        # Her sayfa yüklendiğinde yeni veri çek
        iss_data = fetch_iss_location()
        if iss_data:
            return render(request, 'iss_tracker.html', {'iss_location': iss_data})
        return render(request, 'iss_tracker.html', {'error': 'ISS verisi alınamadı'})
    except Exception as e:
        print(f"ISS Tracker Hatası: {str(e)}")
        return render(request, 'iss_tracker.html', {'error': 'Bir hata oluştu'})

def get_iss_location(request):
    """ISS konum API endpoint'i"""
    try:
        # Canlı veri çek
        iss_data = fetch_iss_location()
        if iss_data:
            data = {
                'latitude': iss_data.latitude,
                'longitude': iss_data.longitude,
                'timestamp': iss_data.timestamp.isoformat(),
                'people_in_space': iss_data.people_in_space
            }
            return JsonResponse(data)
        return JsonResponse({'error': 'ISS verisi alınamadı'}, status=404)
    except Exception as e:
        print(f"ISS API Hatası: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def fetch_live_iss_data():
    """ISS'in canlı konumunu çek"""
    try:
        # ISS konum API'si
        iss_response = requests.get('http://api.open-notify.org/iss-now.json', timeout=5)
        people_response = requests.get('http://api.open-notify.org/astros.json', timeout=5)
        
        if iss_response.status_code == 200 and people_response.status_code == 200:
            iss_data = iss_response.json()
            people_data = people_response.json()
            
            # Yeni konum oluştur ve kaydet
            location = ISSLocation.objects.create(
                latitude=float(iss_data['iss_position']['latitude']),
                longitude=float(iss_data['iss_position']['longitude']),
                people_in_space=people_data['number'],
                timestamp=datetime.now()
            )
            
            print(f"Yeni ISS verisi: Lat={location.latitude}, Long={location.longitude}, People={location.people_in_space}")
            return location
            
    except Exception as e:
        print(f"ISS veri çekme hatası: {str(e)}")
        return None


def solar_system(request):
    # Güneş sistemi verilerini güncelle
    fetch_solar_system_data()
    # Gezegenleri al
    planets = SolarSystemBody.objects.filter(body_type='Planet')
    return render(request, 'solar_system.html', {'planets': planets})


def planet_moons(request):
    # Önce veriyi çek
    fetch_planet_moons()
    # Sonra tüm ayları getir ve sırala
    moons = PlanetMoon.objects.all().order_by('planet_name', 'name')
    print(f"Toplam {moons.count()} uydu bulundu")  # Debug için
    return render(request, 'moons.html', {'moons': moons})

def dwarf_planets(request):
    # Önce veriyi çek
    fetch_dwarf_planets()
    # Sonra cüce gezegenleri getir
    dwarfs = DwarfPlanet.objects.all().order_by('name')
    print(f"Toplam {dwarfs.count()} cüce gezegen bulundu")  # Debug için
    return render(request, 'dwarf_planets.html', {'dwarfs': dwarfs})

def asteroids(request):
    # Önce veriyi çek
    fetch_asteroids()
    # Sonra asteroidleri getir
    asteroids = Asteroid.objects.all().order_by('name')
    print(f"Toplam {asteroids.count()} asteroid bulundu")  # Debug için
    return render(request, 'asteroids.html', {'asteroids': asteroids})

# views.py'a ekle
def astronauts(request):
    fetch_astronauts()  # Astronot verilerini güncelle
    astronauts = Astronaut.objects.filter(status='active')  # Aktif astronotları getir
    return render(request, 'astronauts.html', {'astronauts': astronauts})

