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
# Create your views here.

get_machine_list_url = hosturl + "/api/Masters/machine_list"
get_mould_list_url = hosturl + "/api/Masters/mould_list"
get_product_list_url = hosturl + "/api/Masters/product_list"

def add_production_entry(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            r = requests.post(
                hosturl + "/api/Production/create_production_entry",
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

        # GET → Load dropdowns
        ma=requests.post(get_machine_list_url,data={},headers=headers)
        mo=requests.post(get_mould_list_url,data={},headers=headers)
        p=requests.post(get_product_list_url,data={},headers=headers)

        return render(
            request,
            'Production/add-production-entry.html',
            {
                'machines': ma.json()['data'],
                'moulds':  mo.json()['data'],
                'products':  p.json()['data']
            }
        )

    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')

def production_list(request):
    token = request.session.get('token', False)
    if token:
        return render(
            request,
            'Production/production-list.html'
        )
    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')
def view_production(request, id):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        r = requests.post(
            hosturl + "/api/Production/get_production_entry_by_id",
            data={'id': id},
            headers=headers
        )
        response = r.json()

        return render(
            request,
            'Production/view-production.html',
            {
                'entry': response['data']['entry'],
                'consumptions': response['data']['consumptions']
            }
        )

    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')


def daily_production_report(request):
    token = request.session.get('token', False)
    if token:
        return render(
            request,
            'Production/daily-production-report.html'
        )

    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')



