import json
from django.test import TestCase
from django.http import HttpRequest, QueryDict
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

from ..oauth import OAuthUsp
from .mock import mock_oauth, token, resource, verifier


class OAuthUspTest(TestCase):
    def setUp(self):
        self.obj = OAuthUsp()

    def test_has_attribute_oauth_usp(self):
        self.assertTrue(hasattr(self.obj, 'oauth_usp'))

    @mock_oauth
    def test_get_authorize_redirect(self):
        request = HttpRequest
        setattr(request, 'session', {})
        resp = self.obj.get_authorize_redirect(request)
        expected = 'https://uspdigital.usp.br/wsusuario/oauth/authorize'
        self.assertIn(expected, resp.url)

    @mock_oauth
    def test_get_resource(self):
        request = HttpRequest()
        query = QueryDict(
            'oauth_token=12345oauth&oauth_verifier=12345veriifer')

        request.GET = query

        session = SessionStore()
        setattr(request, 'session', session)

        request_token = dict(
            oauth_token='token123', oauth_token_secret='oauth_token_secret123',
            oauth_verifier='verifier123')
        data = {"data": {"request_token": request_token}}
        request.session['_state_usp_12345oauth'] = data

        resp = self.obj.get_resource(request)
        expected = json.loads(resource)
        self.assertDictEqual(expected, resp)
