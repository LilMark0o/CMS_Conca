import datetime
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Proveedor, Producto
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Create your views here.


def home(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Has iniciado sesión exitosamente')
            return redirect('home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña inválidos')
            return render(request, 'homeNoLog.html', {})
    elif request.user.is_authenticated:
        # Fetch only the products where userAsignado is the current user
        productos = Producto.objects.filter(userAsignado=request.user)
        proveedores = Proveedor.objects.all()
        return render(request, 'home.html', {'productos': productos, 'proveedores': proveedores})
    return render(request, 'homeNoLog.html', {})


def logout_user(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, 'Has cerrado sesión exitosamente')
    return render(request, 'homeNoLog.html', {})


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ese nombre de usuario ya está en uso')
            elif User.objects.filter(email=email).exists():
                messages.error(
                    request, 'Ese correo electrónico ya está en uso')
            else:
                user = User.objects.create_user(
                    username=username, password=password, email=email, first_name=name)
                user.save()
                messages.success(request, 'Te has registrado exitosamente')
                return redirect('home')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
        # If any validation fails, redirect to the home page
        return redirect('home')
    return render(request, 'homeNoLog.html', {})


def producto(request, pk):
    if request.user.is_authenticated:
        user = request.user
        producto = Producto.objects.get(id=pk)
        if user == producto.userAsignado:
            fechaPedido = producto.ultimoPedido
            fechaActual = datetime.datetime.now()
            if fechaPedido is not None:
                # Convert fechaPedido to datetime if it's a date
                if isinstance(fechaPedido, datetime.date):
                    fechaPedido = datetime.datetime.combine(
                        fechaPedido, datetime.datetime.min.time())
                diferencia = fechaActual - fechaPedido
                if diferencia.days > producto.cadaCuantosDias:
                    messages.error(
                        request, 'Deberías pedir este producto nuevamente')
            return render(request, 'producto.html', {'producto': producto})
        else:
            messages.error(
                request, 'No tienes permiso para ver este producto')
            return redirect('home')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def pedirProducto(request, pk):
    if request.user.is_authenticated:
        user = request.user
        producto = Producto.objects.get(id=pk)
        if user == producto.userAsignado:
            sent = sendEmail(user, producto)
            if sent:
                messages.success(request, 'Producto pedido exitosamente')
                producto.ultimoPedido = datetime.datetime.now()
                producto.save()
                return redirect('home')
            else:
                messages.error(request, 'No se pudo enviar el correo')
                return redirect('home')
        else:
            messages.error(
                request, 'No tienes permiso para pedir este producto')
            return redirect('home')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def sendEmail(user, producto):
    try:
        subject = f"Pedido de {producto.nombre}"
        message = f"El cliente {user.first_name} ha pedido el producto {producto.nombre}. El cliente necesita {producto.cantidadPorOrden} unidades, dado que ya pasaron {producto.cadaCuantosDias} días del último pedido."
        reciever = producto.proveedor.email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [reciever, 'ma.ramirez23@uniandes.edu.co'],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(e)
        return False
