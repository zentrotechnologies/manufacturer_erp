from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    path('purchase-invoice', v.purchase_invoice, name='purchase_invoice'),
    path('view-purchase-invoice/<int:id>', v.view_purchase_invoice, name='view_purchase_invoice'),

    path('purchase-order', v.purchase_invoice, name='purchase_invoice'),
    path('add-purchase-invoice', v.add_purchase_invoice, name='add_purchase_invoice'),

]