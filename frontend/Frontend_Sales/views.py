from django.shortcuts import render, redirect, HttpResponse,HttpResponseRedirect
import requests
import os
import json
from datetime import datetime,date,timedelta
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import datetime
from datetime import date
from helpers.validations import hosturl
from django.conf import settings
from decimal import Decimal

# SALES APIs
add_sales_invoice_api = hosturl + "/api/Sales/create_sales_invoice"
get_sales_invoice_api = hosturl + "/api/Sales/get_sales_invoice_by_id"
sales_invoice_list_api = hosturl + "/api/Sales_invoice_list"

# MASTER DATA
get_customer_list_api = hosturl + "/api/User/customer_list"
get_product_list_api = hosturl + "/api/Masters/product_list"



def add_sales_invoice(request):
    token = request.session.get('token', False)
    if not token:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('Frontend_User:login')

    headers = {'Authorization': f'Bearer {token}'}

    # POST → Save Sales Invoice
    if request.method == 'POST':
        data = request.POST.copy()

        r = requests.post(
            add_sales_invoice_api,
            data=data,
            headers=headers
        )

        return HttpResponse(
            json.dumps(r.json()),
            content_type='application/json'
        )

    # GET → Load Page
    customers = requests.get(get_customer_list_api, headers=headers, json={}).json().get('data', [])

    products = requests.post(get_product_list_api,headers=headers,json={}).json().get('data', [])
    company=settings.COMPANY_DETAILS
    return render(
        request,
        'Sales/add-sales-invoice.html',
        {
            'company':company,
            'customers': customers,
            'products': products,
        }
    )
def sales_invoice_list(request):
    token = request.session.get('token', False)
    if not token:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('Frontend_User:login')

    return render(
        request,
        'Sales/sales-invoice-list.html'
    )
    
    
def view_sales_invoice(request, id):
    token = request.session.get('token')
    headers = {'Authorization': f'Bearer {token}'}

    r = requests.post(
        get_sales_invoice_api,
        data={'id': id},
        headers=headers
    )
    
    res = r.json()['data']

    invoice = res['invoice']

    gst_amount = Decimal(invoice['gst_amount'])
    same_state = invoice['same_state']

    context = {
        'invoice': invoice,
        'items': res['items'],
        'company': settings.COMPANY_DETAILS,
        'cgst': gst_amount / 2 if same_state else Decimal('0.00'),
        'sgst': gst_amount / 2 if same_state else Decimal('0.00'),
        'igst': gst_amount if not same_state else Decimal('0.00'),
    }

    return render(
        request,
        'Sales/view-sales-invoice.html',
        context
    )