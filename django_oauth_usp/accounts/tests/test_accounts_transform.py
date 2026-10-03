import json

from django.test import TestCase

from ..transform import Transform, Mapper
from .faker import fake


class TransformTest(TestCase):
    def setUp(self):
        self.obj = Transform()

    def test_has_mapper_attribute(self):
        self.assertTrue(hasattr(self.obj, 'mapper'))

    def test_mapper(self):
        expected = fake.resource_transformed()
        resp = self.obj.transform_data(fake.resource())
        self.assertDictEqual(expected, resp)

    def test_bind_is_saved_as_json(self):
        vinculo = [{'tipoVinculo': 'SERVIDOR', 'nomeSetor': "D'Ávila", 'tipoFuncao': None}]
        resp = self.obj.transform_data({'vinculo': vinculo})
        self.assertEqual(vinculo, json.loads(resp['bind']))

    def test_none_becomes_empty(self):
        resp = self.obj.transform_data({'emailAlternativoUsuario': None})
        self.assertEqual('', resp['alternative_email'])


class MapperTest(TestCase):
    def setUp(self):
        self.obj = Mapper()

    def test_is_instance_of_object(self):
        self.assertIsInstance(self.obj, object)

    def test_get_mapper(self):
        resp = self.obj.get_mapper()
        expected = self.mock_mapper()
        self.assertDictEqual(resp, expected)

    def mock_mapper(self):
        return {
            'loginUsuario': 'login',
            'nomeUsuario': 'name',
            'tipoUsuario': 'user_type',
            'emailPrincipalUsuario': 'main_email',
            'emailAlternativoUsuario': 'alternative_email',
            'emailUspUsuario': 'usp_email',
            'numeroTelefoneFormatado': 'formatted_phone',
            'wsuserid': 'wsuserid',
            'vinculo': 'bind'
        }
