from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import AbstractBaseUser

from ..models import UserModel


class UserModelTest(TestCase):
    def setUp(self):
        self.obj = UserModel()

    def test_is_instance_of_model(self):
        self.assertIsInstance(self.obj, AbstractBaseUser)

    def test_has_parametters(self):
        parametters = ('login', 'name', 'user_type', 'main_email',
                       'alternative_email', 'usp_email',
                       'formatted_phone', 'wsuserid', 'bind', 'is_staff',
                       'is_active', 'date_joined', 'last_login')
        for expected in parametters:
            with self.subTest():
                message = '{} not found.'.format(expected)
                self.assertTrue(hasattr(self.obj, expected), msg=message)

    def test_has_get_full_name_attribute(self):
        self.assertTrue(hasattr(self.obj, 'get_full_name'))

    def test_has_attribute_get_short_name(self):
        self.assertTrue(hasattr(self.obj, 'get_short_name'))

    def test_create_user(self):
        """User must exists on database"""
        self.make_user()
        self.assertTrue(UserModel.objects.exists())

    def test_get_full_name(self):
        user = self.make_user()
        self.assertEqual('Marc Stold Further', user.get_full_name())

    def test_get_short_name(self):
        user = self.make_user()
        self.assertEqual('Marc', user.get_short_name())

    def test_email_user(self):
        user = self.make_user()
        user.email_user(subject='email test', message='message test',
                        from_email='acesso@test.com')
        self.assertTrue(mail.outbox[0])

    def test_get_phone(self):
        user = self.make_user(formatted_phone='3334455')
        self.assertEqual('3334455', user.get_phone())

    def test_is_servidor(self):
        bind = "[{'tipoVinculo': 'ALUNO'}, {'tipoVinculo': 'SERVIDOR'}]"
        user = self.make_user(bind=bind)
        self.assertTrue(user.is_servidor())

    def test_is_servidor_not(self):
        bind = "[{'tipoVinculo': 'ALUNO'}, {'tipoVinculo': 'ALUNO'}]"
        user = self.make_user(bind=bind)
        self.assertFalse(user.is_servidor())

    def test_unidade_is_allowed(self):
        bind = "[{'codigoUnidade': '12'}, {'codigoUnidade': '14', 'tipoVinculo': 'SERVIDOR'}]"
        user = self.make_user(bind=bind)
        self.assertTrue(user.unidade_is_allowed())

    def test_unidade_is_allowed_not(self):
        bind = "[{'codigoUnidade': '12'}, {'codigoUnidade': '13', 'tipoVinculo': 'SERVIDOR'}]"
        user = self.make_user(bind=bind)
        self.assertFalse(user.unidade_is_allowed())

    def test_prepare_json_string(self):
        json_string = "{'nome': 'Marc', 'cargo': None, 'idade': 30}"
        expected = '{"nome": "Marc", "cargo": "None", "idade": 30}'
        actual = self.obj.prepare_json_string(json_string)
        self.assertEqual(actual, expected)

    def test_has_attributes(self):
        attributes = (
            "get_funcao",
            "get_vinculo",
            "get_setor"  
        )

        for attr in attributes:
            with self.subTest():
                message = f"{attr} not found"
                self.assertTrue(hasattr(self.obj, attr), msg=message)

    def test_get_funcao(self):
        vinculo = self.make_vinculo()
        user = self.make_user(**{"bind": str(vinculo)})
        actual = user.get_funcao()
        expected = "Informática"
        self.assertEqual(actual, expected)

    def test_get_vinculo(self):
        vinculo = self.make_vinculo()
        user = self.make_user(**{"bind": str(vinculo)})
        actual = user.get_vinculo()
        expected = ["SERVIDOR", "ALUNOCEU"]
        self.assertEqual(actual, expected)
    
    def test_get_setor(self):
        vinculo = self.make_vinculo()
        user = self.make_user(**{"bind": str(vinculo)})
        actual = user.get_setor()
        exepcted = "GTI-14"
        self.assertEqual(actual, exepcted)

    def make_user(self, **kwargs):
        default = dict(login='4444444', main_email='main@test.com', password='92874',
                       name='Marc Stold Further', user_type='I ')
        data = dict(default, **kwargs)
        return UserModel.objects.create_user(**data)

    def make_vinculo(self):
        return [
            {
                "tipoVinculo":"SERVIDOR",
                "codigoSetor":63,
                "nomeAbreviadoSetor":"GTI-14",
                "nomeSetor":"Gestão da Tecnologia da Informação",
                "codigoUnidade":14,
                "siglaUnidade":"IAG",
                "nomeUnidade":"Instituto de Astronomia, Geofísica e Ciências Atmosféricas",
                "tipoFuncao": "Informática"
            },
            {
                "tipoVinculo":"ALUNOCEU",
                "codigoSetor":0,
                "nomeAbreviadoSetor": None,
                "nomeSetor": None,
                "codigoUnidade":3,
                "siglaUnidade":"EP",
                "nomeUnidade":"Escola Politécnica",
                "tipoFuncao": ""
            }
        ]