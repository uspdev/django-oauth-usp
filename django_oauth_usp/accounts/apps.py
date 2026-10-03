from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'django_oauth_usp.accounts'
    # A migration 0001 foi gerada com AutoField; fixar aqui evita que projetos
    # com DEFAULT_AUTO_FIELD = BigAutoField gerem uma migration para o pacote.
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from django.core import checks

        from .checks import check_allowed_unidades
        checks.register(check_allowed_unidades)
