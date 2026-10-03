from authlib.integrations.base_client import OAuthError
from django.views.generic import View
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render, resolve_url as r
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.conf import settings

from .oauth import OAuthUsp
from .transform import Transform
from .models import UserModel


def is_safe_url(request, url):
    """Só aceita endereços do próprio site, para o login não virar um open redirect."""
    return url_has_allowed_host_and_scheme(
        url, allowed_hosts={request.get_host()}, require_https=request.is_secure())


class OAuthLogin(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(r('accounts:user_detail'))
        self.set_next_url(request)
        # Só pede o token à USP quando de fato vai redirecionar para o login.
        return OAuthUsp().get_authorize_redirect(request)

    def set_next_url(self, request):
        next_url = request.GET.get('next', '/')
        if not is_safe_url(request, next_url):
            next_url = '/'
        request.session['next'] = next_url


accounts_login = OAuthLogin.as_view()


class OAuthAuthorize(View):
    def setup(self, request, *args, **kwargs):
        self.oauth_usp = OAuthUsp()
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.profile = self.oauth_usp.get_resource(request)
            self.data_transform()
        except (OAuthError, ValueError):
            # Login recusado, token expirado ou resposta inválida da USP.
            return HttpResponseBadRequest(
                'Não foi possível concluir o login com a Senha Única USP.')
        if not self.unidade_is_allowed():
            return HttpResponseForbidden(
                'Seu vínculo com a USP não dá acesso a este sistema.')
        self.persist_user()
        if not self.user.is_active:
            return HttpResponseForbidden()
        self.login_user(request)
        return redirect(self.get_redirect_path(request))

    def data_transform(self):
        transform = Transform()
        self.profile = transform.transform_data(self.profile)
        missing = {'login', 'name', 'user_type'} - self.profile.keys()
        if missing:
            raise ValueError(f'Dados ausentes na resposta da USP: {sorted(missing)}')

    def unidade_is_allowed(self):
        """
        Barra quem não é de ALLOWED_UNIDADES antes de gravar os dados e abrir a
        sessão. Usa a mesma regra do middleware, que libera superusuários.
        """
        if UserModel(bind=self.profile.get('bind', '')).unidade_is_allowed():
            return True
        return UserModel.objects.filter(login=self.profile['login'],
                                        is_superuser=True).exists()

    def persist_user(self):
        self.user, create = UserModel.objects.update_or_create_user(
            **self.profile)

    def login_user(self, request):
        # A identidade já foi confirmada pela USP; não há senha a verificar.
        login(request, self.user, backend=settings.AUTHENTICATION_BACKENDS[0])

    def get_redirect_path(self, request):
        next_path = request.session.pop('next', None)
        if next_path and is_safe_url(request, next_path):
            return next_path
        return r('accounts:user_detail')


accounts_authorize = OAuthAuthorize.as_view()


@login_required
def user_detail(request):
    context = {'user': request.user}
    return render(request, 'user.html', context=context)


@require_POST
def user_logout(request):
    """Só por POST (com CSRF), para outro site não conseguir deslogar o usuário."""
    logout(request)
    return redirect(getattr(settings, 'REDIRECT_AFTER_LOGOUT_URL', '/'))
