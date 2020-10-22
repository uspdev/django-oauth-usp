from django.http import HttpResponseForbidden


class OAuthUspMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.alllowed_unidade_or_forbidden(request)

        response = self.get_response(request)

        return response

    def alllowed_unidade_or_forbidden(self, request):
        if not request.user.unidade_is_allowed():
            return HttpResponseForbidden()

        return self.get_response(request)
