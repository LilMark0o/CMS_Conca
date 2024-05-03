from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.


def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'homeNoLog.html', {})
    else:
        user = request.user
        if user.is_authenticated:
            return render(request, 'home.html', {})
        else:
            return render(request, 'homeNoLog.html', {})


def logout_user(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, 'You are now logged out')
    return render(request, 'homeNoLog.html', {})


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        email = request.POST['email']
        name = request.POST['name']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return render(request, 'register.html', {})
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return render(request, 'register.html', {})
                else:
                    user = User.objects.create_user(
                        username=username, password=password, email=email, first_name=name)
                    user.save()
                    messages.success(request, 'You are now registered')
                    return redirect('home')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'homeNoLog.html', {})
