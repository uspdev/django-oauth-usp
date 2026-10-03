from django.shortcuts import resolve_url as r
from django.test import TestCase, override_settings
from django.http import HttpRequest
from django.contrib.sessions.backends.db import SessionStore

from ..middleware import OAuthUspMiddleware
from .faker import data as user_data
from ..models import UserModel


def get_response(request):
    pass


class OAuthUspMiddlewareTest(TestCase):
    def setUp(self):
        self.obj = OAuthUspMiddleware(get_response)

    def test_has_call_attribute(self):
        self.assertTrue(hasattr(self.obj, '__call__'))

    def test_call_(self):
        user_data['bind'] = '[{"codigoUnidade": "10"}]'
        user = UserModel.objects.create_user(**user_data)
        self.client.force_login(user)

        request = HttpRequest()
        setattr(request, 'user', user)

        session = SessionStore()
        setattr(request, 'session', session)

        resp = self.obj.__call__(request)
        self.assertEqual(403, resp.status_code)


@override_settings(ALLOWED_UNIDADES=[14])
class OAuthUspMiddlewareRequestTest(TestCase):
    def make_user(self, bind, **kwargs):
        return UserModel.objects.create_user(**dict(user_data, bind=bind, **kwargs))

    def test_allowed_unidade(self):
        self.client.force_login(self.make_user('[{"codigoUnidade": 14}]'))
        self.assertEqual(200, self.client.get(r('accounts:user_detail')).status_code)

    def test_unidade_contained_in_allowed_is_blocked(self):
        """A unidade 1 passava por estar contida no texto "[14]"."""
        self.client.force_login(self.make_user('[{"codigoUnidade": 1}]'))
        self.assertEqual(403, self.client.get(r('accounts:user_detail')).status_code)

    def test_superuser_without_bind(self):
        root = UserModel.objects.create_superuser(login='root', name='Root', user_type='S',
                                                  main_email='root@usp.br', password='x')
        self.client.force_login(root)
        self.assertEqual(200, self.client.get(r('accounts:user_detail')).status_code)

    def test_blocked_user_can_logout(self):
        self.client.force_login(self.make_user('[{"codigoUnidade": 1}]'))
        resp = self.client.post(r('accounts:logout'))
        with self.subTest():
            self.assertEqual(302, resp.status_code)
            self.assertNotIn('_auth_user_id', self.client.session)
