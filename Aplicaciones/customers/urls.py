from django.urls import path

from . import client_views, views

app_name = "customers"

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_directo'),
    path('contacto/', views.contacto, name='contacto'),
    path('clientes/', client_views.listar_clientes, name='listado_clientes'),
    path('clientes/crear/', client_views.crear_cliente, name='crear_cliente'),
    path('clientes/<str:id_cliente>/', client_views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<str:id_cliente>/editar/', client_views.editar_cliente, name='editar_cliente'),
    path('clientes/<str:id_cliente>/eliminar/', client_views.eliminar_cliente, name='eliminar_cliente'),
]
