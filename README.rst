================
Django OAuth USP
================

Este pacote permite que usuários façam login utilizando a senha única USP.

Além da autenticação OAuth este pacote também possui migrations para o armazenamento dos
usuários no banco de dados.

É recomendado que a estas migrations sejam rodaddas antes de qualquer outra migration, devido
a dificuldade de alteração do model User depois de realizada a primeira migration:
`Using a custom user model when starting a project`__

__ https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project

Quick start
-----------

1. Adicione "django_oauth_usp" em INSTALLED_APPS no arquivo settings.py::

    INSTALLED_APPS = [
        ...
        'polls',
    ]

2. Adicone o Middleware OAuthUspMiddleware::

    MIDDLEWARE = [
        ...
        'django_oauth_usp.accounts.middleware.OAuthUspMiddleware',
    ]

3. No arquivo settings.py, informe o Model que será utilizado para armazenar os usuários::

        AUTH_USER_MODEL= 'django_oauth_usp.UserModel'

4. Defina os parâmetro para OAuth::

    OAUTH_CALLBACK_ID = callback_id_da_aplicação

    AUTHLIB_OAUTH_CLIENTS = {
        'usp': {
            'client_id': meu_client_id,
            'client_secret': meu_secret_key
        }
    }

    #Rota utilizada para a view accounts_authorize
    REDIRECT_URI = /auth/authorize

    #Lista com o código das unidades que poderão ter acesso.
    ALLOWED_UNIDADES = [12, 13, 14]
5. Rode as migrations::

    python manage.py migrate

6. Adicione rotas para as views accounts_login e accounts_authorize::

    urlpatterns = [
        path('login', accounts_login, name='login'),
        path('authorize', accounts_authorize, name='authorize'),
    ]


