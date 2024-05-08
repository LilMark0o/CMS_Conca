from .models import Producto
from django.shortcuts import render, redirect
import datetime
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Proveedor, Producto
from django.core.mail import send_mail
from django.conf import settings

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
        proveedores = Proveedor.objects.filter(userAsignado=request.user)
        productosPorPedir = []
        for producto in productos:
            fechaPedido = producto.ultimoPedido
            fechaActual = datetime.datetime.now()
            if fechaPedido is not None:
                # Convert fechaPedido to datetime if it's a date
                if isinstance(fechaPedido, datetime.date):
                    fechaPedido = datetime.datetime.combine(
                        fechaPedido, datetime.datetime.min.time())
                diferencia = fechaActual - fechaPedido
                if diferencia.days > producto.cadaCuantosDias:
                    productosPorPedir.append(producto)

        return render(request, 'home.html', {'productos': productos, 'proveedores': proveedores, 'productosPorPedir': productosPorPedir})
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
        print("Username: ", username)
        password = request.POST.get('password1', '')
        print("Password: ", password)
        password2 = request.POST.get('password2', '')
        print("Password2: ", password2)
        email = request.POST.get('email', '')
        print("Email: ", email)
        name = request.POST.get('name', '')
        print("Name: ", name)
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


def borrarPedido(request, pk):
    if request.user.is_authenticated:
        user = request.user
        producto = Producto.objects.get(id=pk)
        if user == producto.userAsignado:
            producto.delete()
            messages.success(request, 'Pedido borrado exitosamente')
            return redirect('home')
        else:
            messages.error(
                request, 'No tienes permiso para borrar este pedido')
            return redirect('home')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def borrarProveedor(request, pk):
    if request.user.is_authenticated:
        user = request.user
        proveedor = Proveedor.objects.get(id=pk)
        if user == proveedor.userAsignado:
            proveedor.delete()
            messages.success(request, 'Proveedor borrado exitosamente')
            return redirect('proveedores')
        else:
            messages.error(
                request, 'No tienes permiso para borrar este proveedor')
            return redirect('proveedores')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('proveedores')


def duplicarPedido(request, pk):
    if request.user.is_authenticated:
        user = request.user
        producto = Producto.objects.get(id=pk)
        if user == producto.userAsignado:
            producto.pk = None
            producto.nombre = producto.nombre + ' (Copia)'
            producto.save()
            messages.success(request, 'Pedido duplicado exitosamente')
            return redirect('home')
        else:
            messages.error(
                request, 'No tienes permiso para duplicar este pedido')
            return redirect('home')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def duplicarProveedor(request, pk):
    if request.user.is_authenticated:
        user = request.user
        proveedor = Proveedor.objects.get(id=pk)
        if user == proveedor.userAsignado:
            proveedor.pk = None
            proveedor.nombre = proveedor.nombre + ' (Copia)'
            proveedor.save()
            messages.success(request, 'Proveedor duplicado exitosamente')
            return redirect('proveedores')
        else:
            messages.error(
                request, 'No tienes permiso para duplicar este proveedor')
            return redirect('proveedores')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('proveedores')


def editarPedido(request, pk):
    print("Editing producto")
    if request.user.is_authenticated:
        user = request.user
        producto = Producto.objects.get(id=pk)
        if user == producto.userAsignado:
            if request.method == 'POST':
                producto.nombre = request.POST['nombre']
                producto.precio = request.POST['precio']
                producto.descripcion = request.POST['descripcion']
                producto.cantidadPorOrden = request.POST['cantidadPorOrden']
                producto.cadaCuantosDias = request.POST['cadaCuantosDias']
                fechaParametro = request.POST['ultimoPedido']
                if fechaParametro != '':
                    producto.ultimoPedido = datetime.datetime.strptime(
                        fechaParametro, '%Y-%m-%d')
                    producto.ultimoPedido = producto.ultimoPedido.date()
                producto.proveedor = Proveedor.objects.get(
                    id=request.POST['proveedor'])
                producto.save()
                messages.success(request, 'Producto editado exitosamente')
                return redirect('home')
            return render(request, 'editarProducto.html', {'producto': producto, 'proveedores': Proveedor.objects.all()})
        else:
            messages.error(
                request, 'No tienes permiso para editar este producto')
            return redirect('home')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def editarProveedor(request, pk):
    if request.user.is_authenticated:
        user = request.user
        proveedor = Proveedor.objects.get(id=pk)
        if user == proveedor.userAsignado:
            if request.method == 'POST':
                proveedor.nombre = request.POST['nombre']
                proveedor.direccion = request.POST['direccion']
                proveedor.ciudad = request.POST['ciudad']
                proveedor.telefono = request.POST['telefono']
                proveedor.email = request.POST['email']
                proveedor.save()
                messages.success(request, 'Proveedor editado exitosamente')
                return redirect('proveedores')
            return render(request, 'editarProveedor.html', {'proveedor': proveedor})
        else:
            messages.error(
                request, 'No tienes permiso para editar este proveedor')
            return redirect('proveedores')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def nuevoPedido(request):
    if request.user.is_authenticated:
        user = request.user
        proveedores = Proveedor.objects.filter(userAsignado=user)
        print(len(proveedores))
        if request.method == 'POST':
            nombre = request.POST['nombre']
            precio = request.POST['precio']
            descripcion = request.POST['descripcion']
            cantidadPorOrden = request.POST['cantidadPorOrden']
            cadaCuantosDias = request.POST['cadaCuantosDias']
            fechaParametro = request.POST['ultimoPedido']
            if fechaParametro != '':
                fechaParametro = datetime.datetime.strptime(
                    fechaParametro, '%Y-%m-%d')
                fechaParametro = fechaParametro.date()
            proveedor = Proveedor.objects.get(id=request.POST['proveedor'])
            if (proveedor.userAsignado != user):
                messages.error(
                    request, 'No tienes permiso para crear un pedido para este proveedor')
                return redirect('home')
            elif proveedor is None:
                messages.error(
                    request, 'El proveedor seleccionado no existe')
                return redirect('home')

            producto = Producto.objects.create(
                nombre=nombre, precio=precio, descripcion=descripcion, cantidadPorOrden=cantidadPorOrden, cadaCuantosDias=cadaCuantosDias, ultimoPedido=fechaParametro, proveedor=proveedor, userAsignado=user)
            producto.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('home')
        if len(proveedores) == 0:
            messages.error(
                request, 'No tienes proveedores creados, no puedes crear un producto')
            return redirect('home')
        return render(request, 'nuevoProducto.html', {'proveedores': proveedores})
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def proveedores(request):
    if request.user.is_authenticated:
        user = request.user
        proveedores = Proveedor.objects.filter(userAsignado=user)
        if len(proveedores) > 0:
            return render(request, 'proveedores.html', {'proveedores': proveedores})
        else:
            return render(request, 'proveedores.html', {'proveedores': None})
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def productos(request):
    if request.user.is_authenticated:
        user = request.user
        productos = Producto.objects.filter(userAsignado=user)
        if len(productos) > 0:
            return render(request, 'productos.html', {'productos': productos})
        else:
            return render(request, 'productos.html', {'productos': None})
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def proveedor(request, pk):
    if request.user.is_authenticated:
        user = request.user
        proveedor = Proveedor.objects.get(id=pk)
        if user == proveedor.userAsignado:
            return render(request, 'proveedor.html', {'proveedor': proveedor})
        else:
            messages.error(
                request, 'No tienes permiso para ver este proveedor')
            return redirect('proveedores')
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')


def nuevoProveedor(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            nombre = request.POST['nombre']
            direccion = request.POST['direccion']
            ciudad = request.POST['ciudad']
            telefono = request.POST['telefono']
            email = request.POST['email']
            proveedor = Proveedor.objects.create(
                nombre=nombre, direccion=direccion, ciudad=ciudad, telefono=telefono, email=email, userAsignado=user)
            proveedor.save()
            messages.success(request, 'Proveedor creado exitosamente')
            return redirect('proveedores')
        return render(request, 'nuevoProveedor.html', {})
    else:
        messages.error(request, 'Necesitas iniciar sesión')
        return redirect('home')
