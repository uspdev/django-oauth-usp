from django.conf import settings
from django.core.checks import Error, Warning

ALL_UNIDADES = '__all__'


def check_allowed_unidades(app_configs, **kwargs):
    """
    Mostra no runserver, migrate e check os erros de ALLOWED_UNIDADES que, em
    produção, só apareceriam quando alguém tentasse entrar.
    """
    if not hasattr(settings, 'ALLOWED_UNIDADES'):
        return [Error(
            'ALLOWED_UNIDADES não foi definido.',
            hint=f"Informe a lista de códigos das unidades, ou '{ALL_UNIDADES}' "
                 'para liberar qualquer pessoa com Senha Única USP.',
            id='django_oauth_usp.E001',
        )]

    allowed = settings.ALLOWED_UNIDADES
    if allowed == ALL_UNIDADES:
        return []
    if not isinstance(allowed, (list, tuple, set)):
        return [Error(
            f'ALLOWED_UNIDADES deve ser uma lista de códigos ou '
            f"'{ALL_UNIDADES}', não {allowed!r}.",
            id='django_oauth_usp.E002',
        )]
    if not allowed:
        return [Warning(
            'ALLOWED_UNIDADES está vazio: só superusuários conseguirão entrar.',
            hint=f"Para liberar qualquer pessoa com Senha Única USP, use '{ALL_UNIDADES}'.",
            id='django_oauth_usp.W001',
        )]
    return []
