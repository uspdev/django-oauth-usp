from importlib import import_module

from django.apps import apps
from django.test import TestCase

from ..models import UserModel
from .faker import data as user_data

migration = import_module('django_oauth_usp.accounts.migrations.0002_invalida_senha_wsuserid')


class InvalidaSenhaWsuseridTest(TestCase):
    def test_password_equal_to_wsuserid_is_invalidated(self):
        user = UserModel.objects.create_user(**dict(user_data, login='antigo', wsuserid='ws-1', password='ws-1'))
        migration.invalida_senha_wsuserid(apps, None)
        user.refresh_from_db()
        self.assertFalse(user.has_usable_password())

    def test_other_passwords_are_kept(self):
        user = UserModel.objects.create_user(**dict(user_data, login='admin', wsuserid='ws-2', password='senha-forte'))
        migration.invalida_senha_wsuserid(apps, None)
        user.refresh_from_db()
        self.assertTrue(user.check_password('senha-forte'))
