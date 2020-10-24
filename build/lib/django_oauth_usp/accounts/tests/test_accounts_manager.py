from django.test import TestCase
from django.contrib.auth.models import BaseUserManager

from ..managers import UserManager


class UserManagerTest(TestCase):
    def setUp(self):
        self.obj = UserManager()

    def test_is_instance_of_base_user_manager(self):
        self.assertIsInstance(self.obj, BaseUserManager)
