from django.conf import settings
from authlib.integrations.django_client import OAuth


RESOURCE_URL = '/wsusuario/oauth/usuariousp'


class OAuthSettings:
    def __init__(self):
        self.base_url = 'https://uspdigital.usp.br/wsusuario/oauth'
        self.oauth = OAuth()

    def create(self):
        base_url = self.base_url
        callback_id = getattr(settings, 'OAUTH_CALLBACK_ID')
        self.oauth.register(
            name='usp',
            request_token_url=base_url + '/request_token',
            access_token_url=base_url + '/access_token',
            authorize_url=base_url +
            '/authorize?callback_id={}'.format(callback_id),
            api_base_url='https://uspdigital.usp.br/'
        )
        return self.oauth


class OAuthUsp:
    def __init__(self):
        oauth_usp = OAuthSettings().create()
        self.oauth_usp = oauth_usp.create_client('usp')
        self.redirect_uri = getattr(settings, 'REDIRECT_URI')

    def get_authorize_redirect(self, request):
        oauth_usp = self.oauth_usp
        authorize_redirect = oauth_usp.authorize_redirect(
            request, self.redirect_uri)
        return authorize_redirect

    def get_resource(self, request):
        oauth_usp = self.oauth_usp
        token = oauth_usp.authorize_access_token(request)
        resource = oauth_usp.post(RESOURCE_URL, token=token)
        return resource.json()
