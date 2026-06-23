from django.urls import path
from . import views

app_name = 'autenticacao'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.register_view, name='register'),
]
