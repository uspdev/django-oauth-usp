from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    def _create_user(self, login, name, user_type, main_email, password,
                     is_staff, is_superuser, **extra_fields):

        now = timezone.now()

        self._validate_fields(login=login, name=name, user_type=user_type)
        main_email = self.normalize_email(main_email)

        user = self.model(login=login, name=name, user_type=user_type,
                          main_email=main_email, is_staff=is_staff,
                          is_active=True, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)

        # Usuários do OAuth não têm senha: entram só pela Senha Única USP.
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def _validate_fields(self, login, name, user_type):
        if not login:
            raise ValueError(_('The login must be set.'))
        if not name:
            raise ValueError(_('The name must be set.'))
        if not user_type:
            raise ValueError(_('The type must be set'))

    def create_user(self, login, name, user_type, main_email=None,
                    password=None, **extra_fields):

        return self._create_user(login, name, user_type, main_email,
                                 password, False, False, **extra_fields)

    def update_or_create_user(self, login, name, user_type, main_email=None,
                              password=None, **extra_fields):
        """
        Cria o usuário ou atualiza só os dados de perfil vindos do OAuth.
        Permissões (is_staff, is_superuser), is_active e date_joined são
        definidos apenas na criação, para que o admin possa desativar ou
        promover usuários sem que o próximo login desfaça a alteração.
        """
        self._validate_fields(login=login, name=name, user_type=user_type)

        user = self.filter(login=login).first()
        if user is None:
            user = self._create_user(login, name, user_type, main_email,
                                     password, False, False, **extra_fields)
            return (user, True)

        profile = dict(name=name, user_type=user_type,
                       main_email=self.normalize_email(main_email),
                       **extra_fields)
        for field, value in profile.items():
            setattr(user, field, value)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return (user, False)

    def create_superuser(self, login, name, user_type, main_email,
                         password, **extra_fields):

        return self._create_user(login, name, user_type, main_email, password,
                                 True, True, **extra_fields)
