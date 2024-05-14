from django.contrib import admin

# Register your models here.
from .models import Proveedor, Producto, HistorialPedidos, Notificaciones

admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Notificaciones)
admin.site.register(HistorialPedidos)
