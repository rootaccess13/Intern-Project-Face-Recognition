from django.urls import path
from .views import loginUser, registerUser, logoutUser


urlpatterns = [
    path('l/', loginUser, name='login'),
    path('r/', registerUser, name='register'),
    path('lo/', logoutUser, name='logout'),
]