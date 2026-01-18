from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    
    
    path('vendor_list_pagination_api', vendor_list_pagination_api.as_view(), name = 'vendor_list_pagination_api'),
    path('add_new_vendor', add_new_vendor.as_view(), name = 'add_new_vendor'),
    path('update_vendor', update_vendor.as_view(), name = 'update_vendor'),
    path('get_vendor_by_id', get_vendor_by_id.as_view(), name = 'get_vendor_by_id'),
    path('vendor_list', vendor_list.as_view(), name = 'vendor_list'),
    path('delete_vendor', delete_vendor.as_view(), name = 'delete_vendor'),

    
    path('raw_material_list_pagination_api', raw_material_list_pagination_api.as_view()),
    path('add_new_raw_material', add_new_raw_material.as_view()),
    path('raw_material_list', raw_material_list.as_view()),
    path('get_raw_material_by_id', get_raw_material_by_id.as_view()),
    path('update_raw_material', update_raw_material.as_view()),
    path('delete_raw_material', delete_raw_material.as_view()),
    
    path('machine_list_pagination_api', machine_list_pagination_api.as_view()),
    path('add_new_machine', add_new_machine.as_view()),
    path('machine_list', machine_list.as_view()),
    path('get_machine_by_id', get_machine_by_id.as_view()),
    path('update_machine', update_machine.as_view()),
    path('delete_machine', delete_machine.as_view()),

    path('mould_list_pagination_api', mould_list_pagination_api.as_view()),
    path('add_new_mould', add_new_mould.as_view()),
    path('mould_list', mould_list.as_view()),
    path('get_mould_by_id', get_mould_by_id.as_view()),
    path('update_mould', update_mould.as_view()),
    path('delete_mould', delete_mould.as_view()),

    path('product_list_pagination_api', product_list_pagination_api.as_view()),
    path('add_new_product', add_new_product.as_view()),
    path('product_list', product_list.as_view()),
    path('get_product_by_id', get_product_by_id.as_view()),
    path('update_product', update_product.as_view()),
    path('delete_product', delete_product.as_view()),

]