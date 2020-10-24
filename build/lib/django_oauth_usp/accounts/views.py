from django.views.generic import RedirectView, View
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render, resolve_url as r
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .oauth import OAuthUsp
from .transform import Transform
from .models import UserModel

REDIRECT_AFTER_LOGOUT_URL = getattr(settings, 'REDIRECT_AFTER_LOGOUT_URL')


class OAuthLogin(RedirectView):
    def get(self, request, *args, **kwargs):
        self.detail_if_logedin(request)
        self.set_next_url(request)
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.redirect_uri.url

    def setup(self, request, *args, **kwargs):
        oauth_usp = OAuthUsp()
        self.redirect_uri = oauth_usp.get_authorize_redirect(request)
        return super().setup(request, *args, **kwargs)

    def detail_if_logedin(self, request):
        if request.user.is_authenticated:
            self.redirect_uri = redirect(r('accounts:user_detail'))

    def set_next_url(self, request):
        request.session['next'] = '/'
        if 'next' in request.GET:
            request.session['next'] = request.GET['next']


accounts_login = OAuthLogin.as_view()


class OAuthAuthorize(View):
    def setup(self, request, *args, **kwargs):
        self.oauth_usp = OAuthUsp()
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.profile = self.oauth_usp.get_resource(request)
        self.data_transform()
        self.persist_user()
        self.authenticate_user(request)
        redirect_path = self.get_redirect_path(request)
        return redirect(redirect_path)

    def data_transform(self):
        transform = Transform()
        self.profile = transform.transform_data(self.profile)

    def persist_user(self):
        self.user, create = UserModel.objects.update_or_create_user(
            **self.profile)

    def authenticate_user(self, request):
        user = authenticate(request, username=self.user.login,
                            password=self.user.wsuserid)
        if user:
            login(request=request, user=user)

    def get_redirect_path(self, request):
        next_path = request.session.get('next')
        if next_path:
            return request.session.pop('next')
        return r('accounts:user_detail')


accounts_authorize = OAuthAuthorize.as_view()


@login_required
def user_detail(request):
    context = {'user': request.user}
    return render(request, 'user.html', context=context)


def user_logout(request):
    logout(request)
    return redirect(REDIRECT_AFTER_LOGOUT_URL)
