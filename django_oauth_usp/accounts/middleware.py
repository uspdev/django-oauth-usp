from django.http import HttpResponseForbidden
from django.urls import NoReverseMatch, reverse


class OAuthUspMiddleware:
    """
    Bloqueia usuários logados de unidades fora de ALLOWED_UNIDADES.
    Superusuários (que podem não ter vínculo USP) e o logout são liberados.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        blocked = (user.is_authenticated and not user.is_superuser
                   and not user.unidade_is_allowed())
        if blocked and request.path != self.logout_path():
            return HttpResponseForbidden()

        return self.get_response(request)

    def logout_path(self):
        try:
            return reverse('accounts:logout')
        except NoReverseMatch:
            return None
