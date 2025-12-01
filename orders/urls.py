from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:order_pk>/item/<int:item_pk>/delete/', views.order_item_delete, name='order_item_delete'),
]
