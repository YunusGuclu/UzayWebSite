# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('iss/', views.iss_tracker, name='iss'),
    path('solar-system/', views.solar_system, name='solar_system'),
    path('news/', views.news, name='news'),
    path('planet-moons/', views.planet_moons, name='planet_moons'),
    path('asteroids/', views.asteroids, name='asteroids'),
    path('dwarf-planets/', views.dwarf_planets, name='dwarf_planets'),
    path('astronauts/', views.astronauts, name='astronauts'),
    path('iss/', views.iss_tracker, name='iss'),
    path('api/iss-location/', views.get_iss_location, name='get_iss_location'),
    
]