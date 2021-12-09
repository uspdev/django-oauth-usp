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

        if not password:
            password = extra_fields.get('wsuserid')

        user.set_password(password)
        user.save(using=self.db)
        return user

    def _update_or_create_user(self, login, name, user_type, main_email,
                               password, is_staff, is_superuser,
                               **extra_fields):

        now = timezone.now()
        self._validate_fields(login=login, name=name, user_type=user_type)

        main_email = self.normalize_email(main_email)
        user_data = dict(name=name, user_type=user_type, main_email=main_email,
                         is_staff=is_staff, is_active=True,
                         is_superuser=is_superuser, last_login=now,
                         date_joined=now, **extra_fields)

        user, create = self.model.objects.update_or_create(login=login,
                                                           defaults=user_data)
        if not password:
            password = extra_fields.get('wsuserid')

        user.set_password(password)
        user.save(using=self.db)

        return (user, create)

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
        return self._update_or_create_user(login, name, user_type, main_email,
                                           password, False, False,
                                           **extra_fields)

    def create_superuser(self, login, name, user_type, main_email,
                         password, **extra_fields):

        user = self._create_user(login, name, user_type, main_email, password,
                                 True, True, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user
