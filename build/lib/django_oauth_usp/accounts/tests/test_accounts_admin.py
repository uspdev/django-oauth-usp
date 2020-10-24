from django.test import TestCase
from django.contrib.admin import ModelAdmin

from ..admin import UserModelAdmin
from ..models import UserModel


class UserModelAdminTest(TestCase):
    def setUp(self):
        self.obj = UserModelAdmin(UserModel, UserModelAdmin)

    def test_instance(self):
        self.assertIsInstance(self.obj, ModelAdmin)
