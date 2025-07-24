from django.apps import AppConfig


class ScdAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scd_app'
    verbose_name = 'SCD - Slowly Changing Dimensions' 