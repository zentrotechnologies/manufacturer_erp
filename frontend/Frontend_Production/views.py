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
            data['finished_qty'] = data.get('finished_qty', 0)
            data['rejected_qty'] = data.get('rejected_qty', 0)
            data['batches_made'] = data.get('batches_made', 0)
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
        b = requests.post(hosturl + "/api/Production/batch_list", headers=headers)

        return render(
            request,
            'Production/add-production-entry.html',
            {
                'machines': ma.json()['data'],
                'moulds':  mo.json()['data'],
                'products':  p.json()['data'],
                'batches': b.json()['data']

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
                'entry': response['data'],
                'consumptions': response['data']['consumptions']
            }
        )

    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')


def daily_production_report(request):

    token = request.session.get('token')

    if not token:
        messages.error(request, 'Session expired')
        return redirect('Frontend_User:login')

    headers = {'Authorization': f'Bearer {token}'}

    report_data = []

    if request.method == "POST":

        date = request.POST.get("date")

        r = requests.post(
            hosturl + "/api/Production/daily_production_report",
            data={"date": date},
            headers=headers
        )

        report_data = r.json().get("data", [])

    return render(
        request,
        'Production/daily-production-report.html',
        {"report": report_data}
    )



