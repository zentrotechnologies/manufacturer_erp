from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url


urlpatterns = [
    path('add-sales-invoice',v.add_sales_invoice,name='add_sales_invoice'),

    path('sales-invoice-list',v.sales_invoice_list,name='sales_invoice_list'),

    path('view-sales-invoice/<int:id>', v.view_sales_invoice, name='view_sales_invoice'),  
]