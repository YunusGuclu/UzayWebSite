# models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class SpaceXLaunch(models.Model):
    mission_name = models.CharField(max_length=200)
    launch_date = models.DateTimeField()
    rocket_name = models.CharField(max_length=100)
    launch_success = models.BooleanField(null=True)
    details = models.TextField(null=True, blank=True)
    mission_patch = models.URLField(null=True, blank=True)
    video_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.mission_name

    class Meta:
        ordering = ['-launch_date']

class ISSLocation(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    people_in_space = models.IntegerField(default=0)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"ISS Location at {self.timestamp}"

class SolarSystemBody(models.Model):
    name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    body_type = models.CharField(max_length=100)
    mass = models.FloatField(null=True)
    gravity = models.FloatField(null=True)
    mean_radius = models.FloatField(null=True)
    moons_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class SpaceNews(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    published_date = models.DateTimeField()
    news_url = models.URLField()
    image_url = models.URLField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = "Space News"

# models.py'a eklenecek gezegen modelleri

class PlanetMoon(models.Model):
    """Gezegenlerin Uyduları"""
    name = models.CharField(max_length=100)
    planet_name = models.CharField(max_length=100)
    discovery_date = models.CharField(max_length=100, null=True)
    discovered_by = models.CharField(max_length=200, null=True)
    mass = models.FloatField(null=True)
    radius = models.FloatField(null=True)
    density = models.FloatField(null=True)
    gravity = models.FloatField(null=True)
    is_regular = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.planet_name}'s Moon"

class PlanetRing(models.Model):
    """Gezegen Halkaları"""
    planet_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    discovery_date = models.CharField(max_length=100, null=True)
    discovered_by = models.CharField(max_length=200, null=True)
    composition = models.CharField(max_length=200, null=True)
    inner_radius = models.FloatField(null=True)
    outer_radius = models.FloatField(null=True)

    def __str__(self):
        return f"{self.planet_name} - {self.name}"

class DwarfPlanet(models.Model):
    """Cüce Gezegenler"""
    name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    mass = models.FloatField(null=True)
    radius = models.FloatField(null=True)
    density = models.FloatField(null=True)
    gravity = models.FloatField(null=True)
    escape_velocity = models.FloatField(null=True)
    mean_temperature = models.FloatField(null=True)
    moons_count = models.IntegerField(default=0)
    discovery_date = models.CharField(max_length=100, null=True)
    discovered_by = models.CharField(max_length=200, null=True)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class Asteroid(models.Model):
    """Asteroidler"""
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    body_type = models.CharField(max_length=100)
    mass = models.FloatField(null=True)
    diameter = models.FloatField(null=True)
    density = models.FloatField(null=True)
    gravity = models.FloatField(null=True)
    orbit_period = models.FloatField(null=True)  # Gün cinsinden
    is_potentially_hazardous = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Astronaut(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='active')  # active veya inactive
    agency = models.CharField(max_length=100, blank=True)
    spacecraft = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
