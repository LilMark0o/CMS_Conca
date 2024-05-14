from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Proveedor(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    userAsignado = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return (f"{self.nombre} - {self.email} - {self.telefono}")


class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.FloatField()
    descripcion = models.CharField(max_length=50)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    cadaCuantosDias = models.IntegerField(default=0)
    cantidadPorOrden = models.IntegerField(default=0)
    fecha_registro = models.DateField(auto_now_add=True)
    userAsignado = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    ultimoPedido = models.DateField()
    # imagen = models.ImageField(upload_to='productos', null=True)

    def __str__(self):
        return self.nombre


class HistorialPedidos(models.Model):
    fecha = models.DateField()
    cantidad = models.IntegerField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    userAsignado = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    notificado = models.BooleanField(default=False)

    def __str__(self):
        return (f"{self.fecha} - {self.cantidad} - {self.producto}")


class Notificaciones(models.Model):
    fecha = models.DateField()
    mensaje = models.CharField(max_length=50)
    userAsignado = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    mostrado = models.BooleanField(default=False)
    estadoPedido = models.CharField(max_length=50, default="Rechazado")

    def __str__(self):
        return (f"{self.fecha} - {self.mensaje}")


class ImportantStuff(models.Model):
    account_sid = models.CharField(max_length=50)
    auth_token = models.CharField(max_length=50)
