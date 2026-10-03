from django.contrib import admin

from .models import UserModel


class UserModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'login', 'user_type', 'main_email',
                    'alternative_email', 'usp_email', 'formatted_phone')
    # O campo guarda o hash; editá-lo como texto gravaria a senha sem hash.
    readonly_fields = ('password', 'last_login')


admin.site.register(UserModel, UserModelAdmin)
admin.site.site_header = 'Usuários'
admin.site.site_title = 'Usuários'
admin.site.index_title = 'Usuários'
