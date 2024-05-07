from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('producto/<int:pk>', views.producto, name='producto'),
    path('pedirProducto/<int:pk>', views.pedirProducto, name='pedirProducto'),
    path('borrarPedido/<int:pk>', views.borrarPedido, name='borrarPedido'),
    path('duplicarPedido/<int:pk>', views.duplicarPedido, name='duplicarPedido'),
    path('editarPedido/<int:pk>', views.editarPedido, name='editarPedido'),

]
