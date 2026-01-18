from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('raw_material_inventory_list_pagination_api',raw_material_inventory_list_pagination_api.as_view()),
    path('production_inventory_list_pagination_api',production_inventory_list_pagination_api.as_view()),
]