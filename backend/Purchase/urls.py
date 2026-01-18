from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('create_purchase_invoice', create_purchase_invoice.as_view(), name = 'create_purchase_invoice'),


    path('purchase_invoice_list_pagination_api', purchase_invoice_list_pagination_api.as_view()),
    path('purchase_invoice_list', purchase_invoice_list.as_view()),
    path('get_purchase_invoice_by_id', get_purchase_invoice_by_id.as_view()),
]