from django.contrib import admin

# Register your models here.
from .models import Proveedor, Producto, historialPedidos

admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(historialPedidos)
