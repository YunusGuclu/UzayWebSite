# schedulers.py
from apscheduler.schedulers.background import BackgroundScheduler
from .utils import (
    fetch_spacex_launches, 
    fetch_iss_location,
    fetch_solar_system_data, 
    fetch_space_news,
    fetch_planet_moons,
    fetch_dwarf_planets,
    fetch_asteroids,  
    fetch_astronauts,
)

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # İlk veri çekme işlemleri
    try:
        print("İlk veri çekme işlemleri başlatılıyor...")
        fetch_planet_moons()

        fetch_dwarf_planets()
        fetch_asteroids()
        fetch_astronauts()

    except Exception as e:
        print(f"İlk veri çekme hatası: {e}")

    scheduler.add_job(fetch_spacex_launches, 'interval', minutes=60)
    scheduler.add_job(fetch_iss_location, 'interval', minutes=1)  # fetch_iss_data değil
    scheduler.add_job(fetch_solar_system_data, 'interval', minutes=60)
    scheduler.add_job(fetch_space_news, 'interval', minutes=1)
    scheduler.add_job(fetch_planet_moons, 'interval', hours=24)
    scheduler.add_job(fetch_dwarf_planets, 'interval', hours=24)
    scheduler.add_job(fetch_asteroids, 'interval', hours=24)
    scheduler.add_job(fetch_astronauts, 'interval', hours=24)
    
    scheduler.start()