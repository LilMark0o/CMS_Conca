from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('productos/', views.productos, name='productos'),
    path('producto/<int:pk>', views.producto, name='producto'),
    path('pedirProducto/<int:pk>', views.pedirProducto, name='pedirProducto'),
    path('borrarPedido/<int:pk>', views.borrarPedido, name='borrarPedido'),
    path('duplicarPedido/<int:pk>', views.duplicarPedido, name='duplicarPedido'),
    path('editarPedido/<int:pk>', views.editarPedido, name='editarPedido'),
    path('nuevoProducto/', views.nuevoPedido, name='nuevoProducto'),
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedor/<int:pk>', views.proveedor, name='proveedor'),
    path('nuevoProveedor/', views.nuevoProveedor, name='nuevoProveedor'),
    path('borrarProveedor/<int:pk>', views.borrarProveedor, name='borrarProveedor'),
    path('duplicarProveedor/<int:pk>',
         views.duplicarProveedor, name='duplicarProveedor'),
    path('editarProveedor/<int:pk>', views.editarProveedor, name='editarProveedor'),
    path('confirmarProducto/<int:pk>',
         views.confirmarProducto, name='confirmarProducto'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),

]
