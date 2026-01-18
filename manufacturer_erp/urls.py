"""
URL configuration for manufacturer_erp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # backend
    
    path('api/User/', include('User.urls')),
    path('api/Masters/', include('Masters.urls')),
    path('api/Dashboard/', include('Dashboard.urls')),
    path('api/Inventory/', include('inventory.urls')),
    path('api/Purchase/', include('Purchase.urls')),
    path('api/Production/', include('Production.urls')),
    path('api/Sales/', include('Sales.urls')),
    
    
    
    #frontend
    path('',include(('Frontend_User.urls', 'Frontend_User'),namespace='Frontend_User')),
    path('dashboard/',include(('Frontend_Dashboard.urls', 'Frontend_Dashboard'),namespace='Frontend_Dashboard')),
    path('masters/',include(('Frontend_Masters.urls', 'Frontend_Masters'),namespace='Frontend_Masters')),
    path('purchase/',include(('Frontend_Purchase.urls', 'Frontend_Purchase'),namespace='Frontend_Purchase')),
    path('inventory/',include(('Frontend_Inventory.urls', 'Frontend_Inventory'),namespace='Frontend_Inventory')),
    path('production/',include(('Frontend_Production.urls', 'Frontend_Production'),namespace='Frontend_Production')),
    path('sales/',include(('Frontend_Sales.urls', 'Frontend_Sales'),namespace='Frontend_Sales')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)