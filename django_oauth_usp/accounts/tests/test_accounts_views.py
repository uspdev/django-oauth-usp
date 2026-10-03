from unittest import mock

from authlib.integrations.base_client import OAuthError
from django.contrib.auth import authenticate
from django.test import RequestFactory, TestCase, override_settings
from django.shortcuts import resolve_url as r
from django.http import HttpRequest, QueryDict
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import AnonymousUser
from django.test import Client

from ..views import OAuthAuthorize, OAuthLogin
from ..models import UserModel
from ..oauth import OAuthUsp
from .mock import mock_oauth
from .faker import data as user_data


class LoginViewsTest(TestCase):
    @mock_oauth
    def setUp(self):
        self.resp = self.client.get(r('accounts:login'))

    def test_status_code(self):
        """Status code should be 302"""
        self.assertEqual(302, self.resp.status_code)


class LoginViewsUserLogedInTest(TestCase):
    @mock_oauth
    def setUp(self):
        user_data['bind'] = '[{"codigoUnidade": "14"}]'
        self.user = UserModel.objects.create_user(**user_data)
        self.client.force_login(self.user)
        self.resp = self.client.get(r('accounts:login'))

    def test_redirect_to_user_detail(self):
        """Loged in user should be redirect to user detail"""
        expected = '/user'
        self.assertEqual(self.resp.url, expected)


class AuthorizeViewTest(TestCase):
    @mock_oauth
    def setUp(self):
        self.request = HttpRequest()
        query = QueryDict(
            'oauth_token=12345oauth&oauth_verifier=12345veriifer')

        self.request.GET = query

        session = SessionStore()
        setattr(self.request, 'session', session)

        request_token = dict(
            oauth_token='token123', oauth_token_secret='oauth_token_secret123',
            oauth_verifier='verifier123')
        data = {"data": {"request_token": request_token}}
        self.request.session['_state_usp_12345oauth'] = data

        user = UserModel.objects.create_user(**user_data)
        setattr(user, 'wsuserid', 'oiuasd098')
        setattr(self.request, 'user', user)

        self.obj = OAuthAuthorize()

    @ mock_oauth
    def test_user_has_been_presisted(self):
        self.obj.setup(self.request)
        self.obj.get(self.request)
        self.assertTrue(UserModel.objects.exists())

    @ mock_oauth
    def test_user_loged_in(self):
        self.obj.setup(self.request)
        self.obj.get(self.request)
        self.assertTrue(self.request.user.is_authenticated)

    @ mock_oauth
    def test_response_status_code(self):
        self.obj.setup(self.request)
        resp = self.obj.get(self.request)
        self.assertTrue(302, resp.status_code)


class OAuthLoginTest(TestCase):
    def login(self, **params):
        request = RequestFactory().get(r('accounts:login'), params)
        request.session = SessionStore()
        request.user = AnonymousUser()
        OAuthLogin.as_view()(request)
        return request.session.get('next')

    @mock_oauth
    def test_next_url(self):
        self.assertEqual('/', self.login())

    @mock_oauth
    def test_next_url_same_site(self):
        self.assertEqual('/itens/1?a=b', self.login(next='/itens/1?a=b'))

    @mock_oauth
    def test_next_url_other_site_is_ignored(self):
        for url in ('https://evil.com/', '//evil.com/', 'javascript:alert(1)', '/\\evil.com'):
            with self.subTest(url=url):
                self.assertEqual('/', self.login(next=url))

    def test_does_not_call_usp_when_logged_in(self):
        """Usuário logado vai para os dados da conta sem pedir token à USP."""
        self.client.force_login(UserModel.objects.create_user(**dict(user_data, login='logado')))
        with mock.patch.object(OAuthUsp, 'get_authorize_redirect') as authorize:
            resp = self.client.get(r('accounts:login'))
        with self.subTest():
            self.assertRedirects(resp, r('accounts:user_detail'), fetch_redirect_response=False)
            authorize.assert_not_called()


RESOURCE = {
    'loginUsuario': '1234567',
    'nomeUsuario': 'Ana Pereira',
    'tipoUsuario': 'I',
    'emailPrincipalUsuario': 'ana@usp.br',
    'emailAlternativoUsuario': None,
    'wsuserid': 'ws-ana',
    'vinculo': [{'tipoVinculo': 'SERVIDOR', 'codigoUnidade': 14, 'nomeSetor': "D'Ávila"}],
}


class AuthorizeFlowTest(TestCase):
    def authorize(self, resource=RESOURCE, next_url=None):
        if next_url is not None:
            session = self.client.session
            session['next'] = next_url
            session.save()
        with mock.patch.object(OAuthUsp, 'get_resource', return_value=resource):
            return self.client.get(r('accounts:authorize'))

    def test_login_and_redirect_to_next(self):
        resp = self.authorize(next_url='/itens')
        with self.subTest():
            self.assertRedirects(resp, '/itens', fetch_redirect_response=False)
            self.assertEqual(str(UserModel.objects.get().pk), self.client.session['_auth_user_id'])

    def test_unsafe_next_in_session_is_ignored(self):
        resp = self.authorize(next_url='https://evil.com/')
        self.assertRedirects(resp, r('accounts:user_detail'), fetch_redirect_response=False)

    def test_user_has_no_usable_password(self):
        self.authorize()
        user = UserModel.objects.get()
        with self.subTest():
            self.assertFalse(user.has_usable_password())
            self.assertIsNone(authenticate(username='1234567', password='ws-ana'))

    def test_bind_saved_as_json(self):
        self.authorize()
        self.assertEqual(RESOURCE['vinculo'], UserModel.objects.get().get_bind())

    def test_none_is_saved_as_empty(self):
        self.authorize()
        self.assertEqual('', UserModel.objects.get().alternative_email)

    def test_second_login_keeps_admin_changes(self):
        """Permissões, desativação e data de cadastro não podem ser desfeitas pelo login."""
        self.authorize()
        user = UserModel.objects.get()
        joined = user.date_joined
        UserModel.objects.filter(pk=user.pk).update(is_staff=True, is_superuser=True)
        self.client.logout()
        self.authorize(dict(RESOURCE, nomeUsuario='Ana P. Souza'))
        user.refresh_from_db()
        with self.subTest():
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertEqual(joined, user.date_joined)
            self.assertEqual('Ana P. Souza', user.name)

    def test_inactive_user_is_not_logged_in(self):
        self.authorize()
        UserModel.objects.update(is_active=False)
        self.client.logout()
        resp = self.authorize()
        with self.subTest():
            self.assertEqual(403, resp.status_code)
            self.assertFalse(UserModel.objects.get().is_active)
            self.assertNotIn('_auth_user_id', self.client.session)

    def test_other_unidade_is_not_logged_in(self):
        """Quem não é de ALLOWED_UNIDADES não entra nem tem os dados gravados."""
        vinculo = [{'tipoVinculo': 'ALUNOGR', 'codigoUnidade': 1}]
        resp = self.authorize(dict(RESOURCE, vinculo=vinculo))
        with self.subTest():
            self.assertEqual(403, resp.status_code)
            self.assertFalse(UserModel.objects.exists())
            self.assertNotIn('_auth_user_id', self.client.session)

    def test_without_bind_is_not_logged_in(self):
        resource = {k: v for k, v in RESOURCE.items() if k != 'vinculo'}
        resp = self.authorize(resource)
        with self.subTest():
            self.assertEqual(403, resp.status_code)
            self.assertFalse(UserModel.objects.exists())

    def test_existing_user_moved_to_other_unidade_is_not_logged_in(self):
        """Os dados já gravados não são atualizados com o vínculo novo."""
        self.authorize()
        self.client.logout()
        resp = self.authorize(dict(RESOURCE, nomeUsuario='Outro nome',
                                   vinculo=[{'codigoUnidade': 1}]))
        with self.subTest():
            self.assertEqual(403, resp.status_code)
            self.assertEqual('Ana Pereira', UserModel.objects.get().name)
            self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(ALLOWED_UNIDADES='__all__')
    def test_all_unidades_logs_in_anyone(self):
        resource = {k: v for k, v in RESOURCE.items() if k != 'vinculo'}
        resp = self.authorize(resource)
        with self.subTest():
            self.assertEqual(302, resp.status_code)
            self.assertIn('_auth_user_id', self.client.session)

    def test_superuser_from_other_unidade_is_logged_in(self):
        """Mesma regra do middleware: superusuários são liberados."""
        self.authorize()
        UserModel.objects.update(is_superuser=True)
        self.client.logout()
        resp = self.authorize(dict(RESOURCE, vinculo=[{'codigoUnidade': 1}]))
        with self.subTest():
            self.assertEqual(302, resp.status_code)
            self.assertIn('_auth_user_id', self.client.session)

    def test_oauth_error_is_bad_request(self):
        with mock.patch.object(OAuthUsp, 'get_resource', side_effect=OAuthError('Missing "oauth_token"')):
            resp = self.client.get(r('accounts:authorize'))
        self.assertEqual(400, resp.status_code)

    def test_invalid_resource_is_bad_request(self):
        resp = self.authorize({'nomeUsuario': 'Sem login'})
        with self.subTest():
            self.assertEqual(400, resp.status_code)
            self.assertFalse(UserModel.objects.exists())


class UserDetailViewLogeInTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(**user_data)
        self.client.force_login(self.user)
        self.resp = self.client.get(r('accounts:user_detail'))

    def test_status_code(self):
        self.assertEqual(200, self.resp.status_code)

    def test_authentication_required(self):
        client = Client()
        resp = client.get(r('accounts:user_detail'))
        self.assertEqual(302, resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(self.resp, 'account_main.html')
        self.assertTemplateUsed(self.resp, 'user.html')

    def test_context_has_user(self):
        context = self.resp.context
        self.assertEqual(self.user, context.get('user'))

    def test_template_has_user_data(self):
        user_data_keys = user_data.keys()

        for info in user_data_keys:
            user_info = user_data.get(info)
            excluded = ['bind', 'login', 'wsuserid', 'is_staff',
                        'is_active', 'date_joined']
            if info not in excluded:
                with self.subTest():
                    self.assertContains(self.resp, user_info)


class OAuthLogoutTest(TestCase):
    def setUp(self):
        user = UserModel.objects.create_user(**user_data)
        self.client.force_login(user)
        self.resp = self.client.post(r('accounts:logout'))

    def test_status_code(self):
        self.assertEqual(302, self.resp.status_code)

    def test_user_logged_out(self):
        self.assertFalse(self.resp.wsgi_request.user.is_authenticated)


class OAuthLogoutGetTest(TestCase):
    def test_get_not_allowed(self):
        """Por GET, outro site poderia deslogar o usuário com um <img>."""
        self.client.force_login(UserModel.objects.create_user(**user_data))
        resp = self.client.get(r('accounts:logout'))
        with self.subTest():
            self.assertEqual(405, resp.status_code)
            self.assertIn('_auth_user_id', self.client.session)

    def test_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(UserModel.objects.create_user(**user_data))
        resp = client.post(r('accounts:logout'))
        self.assertEqual(403, resp.status_code)
