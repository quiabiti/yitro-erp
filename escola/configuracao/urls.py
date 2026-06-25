from django.urls import path, include
from . import views

app_name = 'escola'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('secretaria/', include('escola.secretaria.urls')),
    path('pedagogico/', include('escola.pedagogico.urls')),
    path('docente/', include('escola.docente.urls')),
    path('administrativo/', include('escola.administrativo.urls')),
    path('relatorios/', views.relatorios, name='relatorios'),
]