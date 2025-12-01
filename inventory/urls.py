from django.urls import path
from . import views
from . import views_auth

urlpatterns = [
    path('', views.store_home, name='home'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('register/', views.register, name='register'),
    path('login/', views_auth.customer_login, name='login'),
    path('logout/', views_auth.customer_logout, name='logout'),
]
