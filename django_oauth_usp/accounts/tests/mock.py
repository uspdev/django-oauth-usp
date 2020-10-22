import httpretty
import functools


def mock_oauth(fn):
    @functools.wraps(fn)
    @httpretty.activate
    def wrapper(*args, **kwargs):
        register_oauth_uri()
        response = fn(*args, **kwargs)
        return response
    return wrapper


def register_oauth_uri():
    uri_list = mock_oauth_uri()
    for uri in uri_list:
        httpretty.register_uri(
            getattr(httpretty, uri.get('method')),
            uri=uri.get('uri'),
            body=uri.get('body'),
            headers=uri.get('headers')
        )


token = '123456'
secret = '123456789'
verifier = '778899'

resource = '{"loginUsuario":"login_test", "nomeUsuario":"Name test", "tipoUsuario":"I", "emailPrincipalUsuario":"test@test.com"}'


def mock_oauth_uri():
    base_url = 'https://uspdigital.usp.br/wsusuario/oauth'

    return [
        {
            'uri': base_url + '/request_token',
            'method': 'POST',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'body': 'oauth_token={}&oauth_token_secret={}'.format(token, secret),
        },
        {
            'uri': base_url + '/access_token',
            'method': 'POST',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'body': 'oauth_token={}&oauth_token_secret={}&verifier={}'.format(token,
                                                                              secret, verifier),
        },
        {
            'uri': base_url + '/authorize',
            'method': 'POST',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'body': 'oauth_token={}&oauth_token_secret={}&verifier={}'.format(token,
                                                                              secret, verifier),
        },
        {
            'uri': base_url + '/usuariousp',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': resource,
        }
    ]
