from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


# Create your views here.
def loginUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Invalid login credentials or user is not a staff member.')
        except:
            messages.error(request, 'An error occurred during login.')
    
    return render(request, 'authentication/login.html')


def registerUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']

        try:
            user = User.objects.create_user(username=username, password=password, first_name=firstname, last_name=lastname)
            user.save()
            return render(request, 'authentication/login.html')
        except:
            return render(request, 'authentication/register.html')
    return render(request, 'authentication/register.html')

def logoutUser(request):
    logout(request)
    return redirect('/auth/l/')
