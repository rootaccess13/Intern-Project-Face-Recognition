from django.urls import path
from .views import index, gathers, settings, reqdtr

urlpatterns = [
    path('', index, name='index'),
    path('gather/', gathers, name='gather'),
    path('settings/', settings, name='settings'),
    path('reqdtr/', reqdtr, name='reqdtr'),
]