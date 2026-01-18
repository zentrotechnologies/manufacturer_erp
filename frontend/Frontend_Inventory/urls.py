from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    path('raw-material-inventory',v.raw_material_inventory,name='raw_material_inventory'),
    path('production-inventory',v.production_inventory,name='production_inventory'),
]
