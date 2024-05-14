from .models import ImportantStuff, Notificaciones, Producto, HistorialPedidos
from django.shortcuts import render, redirect
import datetime
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Proveedor, Producto
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

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
        historial = HistorialPedidos.objects.filter(
            userAsignado=request.user).order_by('-fecha')
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
        pedidos = pedidosGraph(request)
        notificaciones = Notificaciones.objects.filter(
            userAsignado=user, mostrado=False)
        contextForNow = {'productos': productos, 'proveedores': proveedores,
                         'productosPorPedir': productosPorPedir, 'historial': historial}
        if len(notificaciones) > 0:
            contextForNow['notificacionesNuevas'] = notificaciones

        if len(pedidos) > 0:
            contextForNow.update(pedidos)
        return render(request, 'home.html', contextForNow)
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
        password = request.POST.get('password1', '')
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
            sent = sendWhatsapp(user, producto)
            if sent:
                producto.ultimoPedido = datetime.datetime.now()
                producto.save()
                messages.success(request, 'Producto pedido exitosamente')
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


def sendWhatsapp(user, producto):
    important = ImportantStuff.objects.get(id=1)
    a = important.account_sid
    b = important.auth_token
    print(a)
    print(b)

    try:
        client = Client(a, b)
        # Define el número de teléfono de destino (con el prefijo internacional)
        numero = '3214330135'

        numero_telefono = f"whatsapp:+57{numero}"
        historial = HistorialPedidos.objects.create(
            fecha=datetime.datetime.now(), cantidad=producto.cantidadPorOrden, producto=producto, userAsignado=user)

        historial.save()

        # Escribe el mensaje que deseas enviar
        publicIp = '34.67.1.244:8080'
        # publicIp = '127.0.0.1:8000'
        link = f"http://{publicIp}/confirmarProducto/{historial.id}"

        mensaje = f"El cliente {user.first_name} ha pedido el producto {producto.nombre}. El cliente necesita {producto.cantidadPorOrden} unidades, dado que ya pasaron {producto.cadaCuantosDias} días del último pedido.\nConfirme el pedido aquí:\n{link} "
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=mensaje,
            to=numero_telefono
        )
        print(message.sid)

        return True
    except Exception as e:
        print(e)
        return False


def notificaciones(request):
    user = request.user
    notificacionesNuevas = Notificaciones.objects.filter(
        userAsignado=user, mostrado=False)
    notificaciones = Notificaciones.objects.filter(
        userAsignado=user, mostrado=True)
    for notificacion in notificacionesNuevas:
        notificacion.mostrado = True
        notificacion.save()

    return render(request, 'notificaciones.html', {'notificaciones': notificaciones, 'notificacionesNuevas': notificacionesNuevas})


def confirmarProducto(request, pk):
    try:
        historial = HistorialPedidos.objects.get(id=pk)
    except HistorialPedidos.DoesNotExist:
        messages.error(request, 'No existe ese pedido')
        return redirect('home')
    user = historial.userAsignado
    if request.method == 'POST':
        estadoPedido = request.POST['pedido']
        historial.notificado = True
        historial.save()
        if estadoPedido == 'confirmado':
            notificacion = Notificaciones.objects.create(
                fecha=datetime.datetime.now(),
                mensaje=f"El pedido de {historial.producto.nombre} ha sido confirmado por el proveedor {historial.producto.proveedor.nombre}",
                userAsignado=user,
                estadoPedido='Confirmado'
            )
            notificacion.save()
            messages.success(request, 'Pedido confirmado exitosamente')
        elif estadoPedido == 'rechazado':
            notificacion = Notificaciones.objects.create(
                fecha=datetime.datetime.now(),
                mensaje=f"El pedido de {historial.producto.nombre} ha sido rechazado por el proveedor {historial.producto.proveedor.nombre}",
                userAsignado=user,
                estadoPedido='Rechazado'
            )
            notificacion.save()
            messages.success(request, 'Pedido rechazado exitosamente')
        elif estadoPedido == 'pendiente':
            notificacion = Notificaciones.objects.create(
                fecha=datetime.datetime.now(),
                mensaje=f"El pedido de {historial.producto.nombre} ha sido puesto en pendiente por el proveedor {historial.producto.proveedor.nombre}",
                userAsignado=user,
                estadoPedido='Pendiente'
            )
            notificacion.save()
            messages.success(
                request, 'Pedido puesto en pendiente exitosamente')
        else:
            messages.error(request, 'Estado de pedido inválido')
        return redirect('home')
    else:
        context = {'historial': historial, 'user': user,
                   'proveedor': historial.producto.proveedor}
        return render(request, 'confirmarProducto.html', context)


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
            return render(request, 'editarProducto.html', {'producto': producto, 'proveedores': Proveedor.objects.filter(userAsignado=user)})
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


def pedidosGraph(request):
    user = request.user
    historial = HistorialPedidos.objects.filter(
        userAsignado=user).order_by('-fecha')
    pedidosList = []
    pedidosDict = {}
    for pedido in historial:
        if pedido.producto.nombre not in pedidosList:
            pedidosList.append(pedido.producto.nombre)
        if pedido.producto.nombre in pedidosDict:
            pedidosDict[pedido.producto.nombre] += pedido.cantidad
        else:
            pedidosDict[pedido.producto.nombre] = pedido.cantidad
    pedidosListOrderedCool = []
    for parameter in pedidosList:
        pedidosListOrderedCool.append(pedidosDict[parameter])
    cs_no = 2
    ce_no = 3
    se_no = 6
    sec_no = 2
    number_list = [cs_no, ce_no, se_no, sec_no]
    context = {'course_list': pedidosList,
               'number_list': pedidosListOrderedCool}
    if len(pedidosList) == 0:
        return {}
    else:
        return context
