from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    # path('accessDenied',v.accessDenied, name='accessDenied'),
    # path('admin/', admin.site.urls),
    path('vendor', v.vendor, name='vendor'),
    path('vendors_list', v.vendor, name='vendors_list'),
    path('add-vendor', v.add_vendor, name='add_vendor'),
    path('edit-vendor/<str:id>', v.edit_vendor, name='edit_vendor'),

    path('raw-material', v.raw_material, name='raw-materials_list'),
    path('add-raw-material', v.add_raw_material, name='add_raw-material'),
    path('edit-raw-material/<str:id>', v.edit_raw_material, name='edit_raw-material'),



    path('machine', v.machine, name='machines_list'),
    path('add-machine', v.add_machine, name='add_machine'),
    path('edit-machine/<str:id>', v.edit_machine, name='edit_machine'),

    path('mould', v.mould, name='mould'),
    path('add-mould', v.add_mould, name='add_mould'),
    path('edit-mould/<int:id>', v.edit_mould, name='edit_mould'),
    
    
    path('product', v.product, name='product'),
    path('add-product', v.add_product, name='add_product'),
    path('edit-product/<int:id>', v.edit_product, name='edit_product'),

]