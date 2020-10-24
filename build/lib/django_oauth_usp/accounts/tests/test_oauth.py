import json
from django.test import TestCase
from authlib.integrations.django_client.integration import DjangoRemoteApp
from django.http import HttpRequest, QueryDict
from django.conf import settings

from ..oauth import OAuthUsp
from .mock import mock_oauth, token, resource, verifier


class OAuthUspTest(TestCase):
    def setUp(self):
        self.obj = OAuthUsp()

    def test_has_attribute_oauth_usp(self):
        self.assertTrue(hasattr(self.obj, 'oauth_usp'))

    def test_oauth_usp_instance(self):
        self.assertIsInstance(self.obj.oauth_usp, DjangoRemoteApp)

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
        resp = self.obj.get_resource(request)
        expected = json.loads(resource)
        self.assertDictEqual(expected, resp)
