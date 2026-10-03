from django.contrib.auth.hashers import check_password, make_password
from django.db import migrations


def invalida_senha_wsuserid(apps, schema_editor):
    """
    Até a versão 1.x, usuários do OAuth recebiam o wsuserid como senha, o que
    permitia entrar por formulários de senha (como o do admin) sabendo o login
    e o wsuserid. Torna inutilizáveis as senhas iguais ao wsuserid; senhas
    definidas de outra forma (createsuperuser) não são alteradas.
    """
    UserModel = apps.get_model('accounts', 'UserModel')
    users = UserModel.objects.exclude(wsuserid='').exclude(password__startswith='!')
    for user in users.iterator():
        if check_password(user.wsuserid, user.password):
            user.password = make_password(None)
            user.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(invalida_senha_wsuserid, migrations.RunPython.noop),
    ]
