from django.urls import path
from .views import index, gathers, settings

urlpatterns = [
    path('', index, name='index'),
    path('gather/', gathers, name='gather'),
    path('settings/', settings, name='settings'),
]