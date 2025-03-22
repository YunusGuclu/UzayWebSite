from django.apps import AppConfig

class UzayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Uzay'

    def ready(self):
        try:
            from .schedulers import start_scheduler
            start_scheduler()  
        except Exception as e:
            print(f"Scheduler başlatılamadı: {e}")