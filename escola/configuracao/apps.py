from django.apps import AppConfig

class ConfiguracaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'escola.configuracao'
    label = 'escola_configuracao'
    verbose_name = 'Configuracao'
