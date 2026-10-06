from django.conf import settings
from django.core.checks import Error, Warning


def check_allowed_unidades(app_configs, **kwargs):
    """
    Mostra no runserver, migrate e check os erros de ALLOWED_UNIDADES que, em
    produção, só apareceriam quando alguém tentasse entrar.
    """
    if not hasattr(settings, 'ALLOWED_UNIDADES'):
        return [Error(
            'ALLOWED_UNIDADES não foi definido.',
            hint='Informe a lista de códigos das unidades, ou [0] para liberar '
                 'qualquer pessoa com Senha Única USP.',
            id='django_oauth_usp.E001',
        )]

    allowed = settings.ALLOWED_UNIDADES
    if not isinstance(allowed, (list, tuple, set)):
        return [Error(
            f'ALLOWED_UNIDADES deve ser uma lista de códigos, não {allowed!r}.',
            id='django_oauth_usp.E002',
        )]
    if not allowed:
        return [Warning(
            'ALLOWED_UNIDADES está vazio: só superusuários conseguirão entrar.',
            hint='Para liberar qualquer pessoa com Senha Única USP, use [0].',
            id='django_oauth_usp.W001',
        )]
    return []
