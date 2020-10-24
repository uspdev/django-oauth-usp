from django.urls import path

from .views import accounts_login, accounts_authorize, user_detail, user_logout


app_name = 'accounts'

urlpatterns = [
    path('login', accounts_login, name='login'),
    path('authorize', accounts_authorize, name='authorize'),
    path('user', user_detail, name='user_detail'),
    path('logout', user_logout, name='logout')
]
