from django.urls import path, include

urlpatterns = [
    path('', include('django_oauth_usp.accounts.urls'))
]


