from django.test import TestCase
from django.shortcuts import resolve_url as r
from django.http import HttpRequest, QueryDict
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import AnonymousUser
from django.test import Client

from ..views import OAuthAuthorize, OAuthLogin
from ..models import UserModel
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
            'oauth_token=12345oauth & oauth_verifier=12345veriifer')

        self.request.GET = query

        session = SessionStore()
        setattr(self.request, 'session', session)

        request_token = dict(
            oauth_token='token123', oauth_token_secret='oauth_token_secret123',
            oauth_verifier='verifier123')
        self.request.session['_usp_authlib_request_token_'] = request_token

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
    def setUp(self):
        self.obj = OAuthLogin()

    @mock_oauth
    def test_next_url(self):
        request = HttpRequest()
        session = SessionStore()

        setattr(request, 'session', session)
        setattr(request, 'user', AnonymousUser())

        self.obj.setup(request)
        self.obj.get(request)

        expected = '/'
        self.assertEqual(self.obj.request.session.get('next'), expected)


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
        self.assertTemplateUsed(self.resp, 'main.html')
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
        self.resp = self.client.get(r('accounts:logout'))

    def test_status_code(self):
        self.assertEqual(302, self.resp.status_code)

    def test_user_logged_out(self):
        self.assertFalse(self.resp.wsgi_request.user.is_authenticated)
