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



get_raw_material_list_url = hosturl + "/api/Masters/raw_material_list"
get_vendor_list_url = hosturl + "/api/Masters/vendor_list"
get_purchase_invoice_url=hosturl + "/api/Purchase/get_purchase_invoice_by_id"
# Create your views here.
def purchase_invoice(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Purchase/purchase_invoice/purchase-invoice-list.html')
    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')


def view_purchase_invoice(request, id):
    token = request.session.get('token', False)
    if not token:
        messages.error(request, 'Session expired')
        return redirect('Frontend_User:login')

    headers = {'Authorization': f'Bearer {token}'}

    r = requests.post(
        get_purchase_invoice_url,
        data={'id': id},
        headers=headers
    )
    res = r.json()

    invoice = res['data']['invoice']      # DICT
    items = res['data']['items']          # LIST


    gst_amount = Decimal(invoice.get('gst_amount', '0'))
    same_state = invoice.get('same_state', True)
    context = {
        'invoice': invoice,
        'items': items,
        'company': settings.COMPANY_DETAILS,  # or however you pass it
        'cgst': gst_amount / 2 if same_state else 0,
        'sgst': gst_amount / 2 if same_state else 0,
        'igst': gst_amount if not same_state else 0,
    }
    print('context',context['company'])
    return render(
        request,
        'Purchase/purchase_invoice/view-purchase-invoice.html',
        context
    )



def add_purchase_invoice(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            r = requests.post(
                hosturl + "/api/Purchase/create_purchase_invoice",
                data=data,
                headers=headers
            )

            try:
                response = r.json()
            except ValueError:
                response = {
                    "response": {
                        "n": 0,
                        "msg": "Server error",
                        "status": "error"
                    }
                }

            return HttpResponse(
                json.dumps(response),
                content_type='application/json'
            )

        # GET → load form
        v=requests.post(get_vendor_list_url,data={},headers=headers)
        r=requests.post(get_raw_material_list_url,data={},headers=headers)

        return render(
            request,
            'Purchase/purchase_invoice/add-purchase-invoice.html',
            {
                'vendors': v.json()['data'],
                'raw_materials': r.json()['data']
            }
        )

    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')
