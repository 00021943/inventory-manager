"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from inventory.api import ProductViewSet, CategoryViewSet
from orders.api import OrderViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    # Django admin disabled - use /panel/ instead
    # path('admin/', admin.site.urls),
    path('panel/', include('panel.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
    path('orders/', include('orders.urls')),
    path('', include('inventory.urls')),
]

# Serve media files in development only
# Static files are served by WhiteNoise in production (configured in settings.py)
# Media files should be served by a web server (nginx) or CDN in production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

