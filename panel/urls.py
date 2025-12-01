from django.urls import path
from . import views
from . import views_auth

app_name = 'panel'

urlpatterns = [
    path('login/', views_auth.panel_login, name='panel_login'),
    path('logout/', views_auth.panel_logout, name='panel_logout'),
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.order_management, name='order_management'),
    path('orders/<int:pk>/', views.order_detail_panel, name='order_detail'),
    path('orders/<int:pk>/status/<str:status>/', views.update_order_status, name='update_order_status'),
    path('inventory/', views.inventory_management, name='inventory_management'),
    path('inventory/<int:pk>/update-stock/', views.update_stock, name='update_stock'),
    path('products/', views.product_management, name='product_management'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('categories/', views.category_management, name='category_management'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('staff/', views.staff_management, name='staff_management'),
    path('staff/create/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),
    path('staff/<int:pk>/toggle-status/', views.staff_toggle_status, name='staff_toggle_status'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    path('customers/', views.customer_management, name='customer_management'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/toggle-status/', views.customer_toggle_status, name='customer_toggle_status'),
]
