from django.conf import settings
from django.test import SimpleTestCase, override_settings

from ..checks import check_allowed_unidades


class CheckAllowedUnidadesTest(SimpleTestCase):
    def ids(self):
        return [message.id for message in check_allowed_unidades(None)]

    def test_valid(self):
        for allowed in ([14], (12, 13), ['14'], [0]):
            with self.subTest(allowed=allowed), override_settings(ALLOWED_UNIDADES=allowed):
                self.assertEqual([], self.ids())

    @override_settings()
    def test_missing(self):
        del settings.ALLOWED_UNIDADES
        self.assertEqual(['django_oauth_usp.E001'], self.ids())

    def test_invalid_type(self):
        for allowed in (14, '14', 'all', '__all__', None):
            with self.subTest(allowed=allowed), override_settings(ALLOWED_UNIDADES=allowed):
                self.assertEqual(['django_oauth_usp.E002'], self.ids())

    @override_settings(ALLOWED_UNIDADES=[])
    def test_empty(self):
        self.assertEqual(['django_oauth_usp.W001'], self.ids())
