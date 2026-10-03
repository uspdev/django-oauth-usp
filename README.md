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

6. Inclua as rotas do pacote (login, authorize, user e logout, no namespace `accounts`)::

    ```
    urlpatterns = [
        path('auth/', include('django_oauth_usp.accounts.urls')),
    ]
    ```

    `REDIRECT_URI` deve apontar para a rota `authorize` (no exemplo, `/auth/authorize`).
    Opcionalmente, defina `REDIRECT_AFTER_LOGOUT_URL` (padrão: `/`).

## Login e logout

* Quem não tem vínculo com uma unidade de `ALLOWED_UNIDADES` recebe 403 já no
  retorno da Senha Única: o usuário não é gravado nem logado. Superusuários já
  cadastrados são liberados. O `OAuthUspMiddleware` continua barrando quem já
  estava logado, por exemplo depois de uma mudança na lista.
* O parâmetro `next` do login (`/auth/login?next=/pagina`) só é aceito para
  endereços do próprio site; qualquer outro é trocado por `/`.
* O logout só aceita POST com o token CSRF:

    ```
    <form method="post" action="{% url 'accounts:logout' %}">
        {% csrf_token %}
        <button type="submit">Sair</button>
    </form>
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

## Atualizando da versão 1.x

A versão 2.0.0 corrige falhas de segurança e muda alguns comportamentos:

* **Logout só por POST.** Troque links `<a href="{% url 'accounts:logout' %}">` por um formulário (veja acima).
* **Sem senha para usuários do OAuth.** Antes, o `wsuserid` era gravado como senha, o que
  permitia entrar por formulários de senha (como o do admin). A migration `0002` torna
  essas senhas inutilizáveis; senhas criadas com `createsuperuser` são mantidas.
  O `migrate` calcula um hash por usuário, então pode levar alguns segundos em bases grandes.
* **O login não sobrescreve mais `is_staff`, `is_superuser`, `is_active` e `date_joined`.**
  Usuários desativados no admin continuam bloqueados (recebem 403 no login).
* **`ALLOWED_UNIDADES` compara os códigos exatos.** Antes, a unidade 1 era aceita quando
  14 estava na lista. O middleware libera superusuários e o logout.
* **Quem não é das unidades permitidas não entra.** Antes, o login era concluído, o
  usuário era gravado e só o middleware respondia 403 nas páginas seguintes, sem
  deixar a pessoa sair. Agora o `authorize` responde 403 sem gravar nem logar.
* **O vínculo é gravado em JSON.** Registros antigos continuam sendo lidos. O método
  `prepare_json_string` foi removido.
* Erros no retorno do OAuth (login recusado, token expirado) respondem 400 em vez de 500.

## Desenvolvimento

O projeto usa o [uv](https://docs.astral.sh/uv/):

```
uv sync
uv run python manage.py test
uv build
```
