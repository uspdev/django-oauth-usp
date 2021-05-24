import json
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings

from .managers import UserManager


class UserModel(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(_("login"), max_length=50, unique=True)
    name = models.CharField(_("name"), max_length=100)
    user_type = models.CharField(_("user type"), max_length=1)
    main_email = models.EmailField(_("main email"), max_length=50)
    alternative_email = models.EmailField(_("alternative email"),
                                          max_length=254)
    usp_email = models.EmailField(_("email usp"), max_length=254)
    formatted_phone = models.CharField(_("phone"), max_length=50)
    wsuserid = models.CharField(_("wsuserid"), max_length=1024)
    bind = models.TextField(_("bind"))
    is_staff = models.BooleanField(_("is staff"))
    is_active = models.BooleanField(_("is active"))
    date_joined = models.DateTimeField(_("Joined at"), auto_now_add=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name', 'user_type', 'main_email']
    EMAIL_FIELD = 'main_email'
    ALLOWED_UNIDADES = str(settings.ALLOWED_UNIDADES)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    objects = UserManager()

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        names = self.name.split()
        return names[0]

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.main_email])

    def get_phone(self):
        return self.formatted_phone

    def is_servidor(self):
        bind = self.get_bind()
        for item in bind:
            if item["tipoVinculo"] == 'SERVIDOR':
                return True

        return False

    def unidade_is_allowed(self):
        bind = self.get_bind()
        for item in bind:
            codigo_unidade = item["codigoUnidade"]
            if str(codigo_unidade) in self.ALLOWED_UNIDADES:
                return True

        return False

    def get_bind(self):
        bind = self.bind.replace("'", '"')
        return json.loads(bind)
