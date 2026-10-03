# Changelog

Todas as mudanças relevantes deste projeto são registradas neste arquivo.

## [2.0.0] - 2026-10-03

Esta versão corrige falhas de segurança no login com a Senha Única USP.
**Recomendamos atualizar.** Há mudanças incompatíveis com a 1.x.

### ⚠️ Ao atualizar

1. Rode `python manage.py migrate`. A migration `0002` invalida as senhas
   antigas dos usuários do OAuth. Ela calcula um hash por usuário, então pode
   levar alguns segundos em bases grandes.
2. Troque os links de logout por um formulário POST:

   ```html
   <form method="post" action="{% url 'accounts:logout' %}">
       {% csrf_token %}
       <button type="submit">Sair</button>
   </form>
   ```

3. Se o seu código usava `prepare_json_string`, troque por `user.get_bind()`,
   que já devolve a lista de vínculos.
4. Confira a lista `ALLOWED_UNIDADES`, porque a comparação agora é exata.

### Segurança

- Os usuários do OAuth não têm mais senha. Antes, o `wsuserid` era gravado como
  senha, e quem soubesse o login e o `wsuserid` de alguém conseguia entrar pelo
  admin ou por outro formulário de senha. As senhas criadas com
  `createsuperuser` são mantidas.
- O parâmetro `next` do login só aceita endereços do próprio site. Antes,
  `/login?next=https://site-malicioso` redirecionava o usuário para fora depois
  do login.
- O logout só aceita POST com o token CSRF. Antes, outro site conseguia deslogar
  o usuário só com uma imagem.
- O login não desfaz mais o que foi alterado no admin: `is_staff`,
  `is_superuser`, `is_active` e `date_joined` são definidos apenas na criação do
  usuário. Usuários desativados continuam bloqueados e recebem 403 no login.
- `ALLOWED_UNIDADES` compara os códigos exatos. Antes, a unidade 1 era aceita
  quando 14 estava na lista.
- Quem não tem vínculo com uma unidade de `ALLOWED_UNIDADES` não entra mais no
  sistema. Antes, o login era concluído e o usuário era gravado; só o middleware
  respondia 403 nas páginas seguintes, sem deixar a pessoa sair. Agora o retorno
  da Senha Única responde 403, sem gravar o usuário nem abrir a sessão.
  Superusuários já cadastrados são liberados.
- O campo de senha é somente leitura no admin. Editá-lo como texto gravaria a
  senha sem hash.

### Alterado

- O middleware libera superusuários, que podem não ter vínculo USP. Também
  libera a rota de logout, para que um usuário bloqueado consiga sair.
- O vínculo é gravado em JSON. Os registros antigos continuam sendo lidos
  normalmente.
- Valores ausentes vindos da USP são gravados como texto vazio, e não mais como
  `"None"`.
- Erros no retorno do OAuth (login recusado, token expirado, resposta
  incompleta) respondem 400 em vez de 500.
- `REDIRECT_AFTER_LOGOUT_URL` passou a ser opcional. O padrão é `/`.
- Django ≥ 4.2 passou a ser dependência declarada do pacote. Também são
  necessários Authlib ≥ 1.3.1 e requests ≥ 2.32.
- Python 3.10 a 3.13, testados na CI.
- O projeto passou a usar o [uv](https://docs.astral.sh/uv/) no lugar do
  Poetry.

### Corrigido

- `get_funcao()`, `get_setor()` e `is_servidor()` não dão mais erro quando o
  usuário não tem vínculo de servidor. Nesse caso retornam `None` ou `False`.
- `get_bind()` não quebra mais com nomes que têm apóstrofo, como "D'Ávila".
- `get_short_name()` não quebra mais com nome vazio.
- O login não pede mais um token à USP quando o usuário já está logado.
- Projetos com `DEFAULT_AUTO_FIELD = BigAutoField` não geram mais uma migration
  para o pacote.

### Removido

- O método `UserModel.prepare_json_string`.
- O logout por GET.

[2.0.0]: https://github.com/uspdev/django-oauth-usp/compare/1.2.2...2.0.0
