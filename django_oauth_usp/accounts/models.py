import ast
import json

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
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

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    objects = UserManager()

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        names = self.name.split()
        return names[0] if names else ''

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.main_email])

    def get_phone(self):
        return self.formatted_phone

    def is_servidor(self):
        return self._get_bind_servidor() is not None

    def unidade_is_allowed(self):
        """Compara os códigos exatos: a unidade 1 não pode passar por estar contida em 14."""
        allowed = {str(codigo) for codigo in settings.ALLOWED_UNIDADES}
        return any(str(item.get('codigoUnidade')) in allowed
                   for item in self.get_bind())

    def get_bind(self):
        """
        Vínculos do usuário como lista de dicts. Aceita JSON e, para registros
        gravados pelas versões anteriores, o repr do Python. Vínculo vazio ou
        inválido (como o de um superusuário criado pelo createsuperuser) vira [].
        """
        if not self.bind:
            return []
        try:
            bind = json.loads(self.bind)
        except ValueError:
            try:
                bind = ast.literal_eval(self.bind)
            except (ValueError, SyntaxError):
                return []
        if not isinstance(bind, list):
            return []
        return [item for item in bind if isinstance(item, dict)]

    def _get_bind_servidor(self):
        return next((item for item in self.get_bind()
                     if item.get('tipoVinculo') == 'SERVIDOR'), None)

    def get_funcao(self):
        servidor = self._get_bind_servidor() or {}
        return servidor.get('tipoFuncao') or None

    def get_vinculo(self):
        return [item.get('tipoVinculo') for item in self.get_bind()]

    def get_setor(self):
        servidor = self._get_bind_servidor() or {}
        return servidor.get('nomeAbreviadoSetor') or None
