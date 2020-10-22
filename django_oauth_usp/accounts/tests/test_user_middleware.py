from django.test import TestCase
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
