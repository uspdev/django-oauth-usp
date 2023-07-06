# Django OAuth USP


Este pacote permite que usuários façam login utilizando a senha única USP.

Além da autenticação OAuth este pacote também possui migrations para o armazenamento dos
usuários no banco de dados.

É recomendado que a estas migrations sejam rodadas antes de qualquer outra migration, devido
a dificuldade de alteração do model User depois de realizada a primeira migration:

*[Using a custom user model when starting a project](https://docs.djangoproject.com/en/4.2/topics/auth/customizing/)*

## Como usar

1. Adicione "django_oauth_usp" em INSTALLED_APPS no arquivo settings.py
    ```
    INSTALLED_APPS = [
        ...
        'django_oauth_usp.accounts',
    ]
    ```

2. Adicone o Middleware OAuthUspMiddleware

    ```
    MIDDLEWARE = [
        ...
        'django_oauth_usp.accounts.middleware.OAuthUspMiddleware',
    ]
    ```

3. No arquivo settings.py, informe o Model que será utilizado para armazenar os usuários

        ```
        AUTH_USER_MODEL= 'accounts.UserModel'
        ```

4. Defina os parâmetro para OAuth::

    ```
    OAUTH_CALLBACK_ID = 'callback_id_da_aplicação'

    AUTHLIB_OAUTH_CLIENTS = {
        'usp': {
            'client_id': 'meu_client_id',
            'client_secret': 'meu_secret_key'
        }
    }
    
    #Rota utilizada para a view accounts_authorize
    REDIRECT_URI = '/auth/authorize'

    #Lista com o código das unidades que poderão ter acesso.
    ALLOWED_UNIDADES = [12, 13, 14]
    ```

5. Rode as migrations::

    ```
    python manage.py migrate
    ```

6. Adicione rotas para as views accounts_login e accounts_authorize::

    ```
    urlpatterns = [
        path('login', accounts_login, name='login'),
        path('authorize', accounts_authorize, name='authorize'),
    ]
    ```
## Dados do usuário

Os model UserModel provê os seguintes dados do usuário
* Nome completo
```
user.get_full_name()
```
* Primeiro nome()
```
user.get_short_name()
```
* Email
```
user.email_user()
```
* Telefone
```
user.get_phone()
```
* É servidor
```
user.is_servidor()
```
* Função
```
user.get_funcao()
```
* Vínculo
```
user.get_vinculo()
```
* Setor
```
user.get_setor()
```