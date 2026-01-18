from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('create_sales_invoice', create_sales_invoice.as_view(), name = 'create_sales_invoice'),
    path('sales_invoice_list_pagination_api',sales_invoice_list_pagination_api.as_view(),name='sales_invoice_list_pagination_api'),
    path("get_sales_invoice_by_id",get_sales_invoice_by_id.as_view(),name="get_sales_invoice_by_id")

    
]