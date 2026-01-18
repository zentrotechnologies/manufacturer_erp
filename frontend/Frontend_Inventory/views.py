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
def raw_material_inventory(request):
    token = request.session.get('token', False)
    if token:
        return render(
            request,
            'Inventory/raw-material-inventory-list.html'
        )

    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')
def production_inventory(request):
    token = request.session.get('token', False)
    if token:
        return render(
            request,
            'Inventory/production-inventory-list.html'
        )

    messages.error(request, 'Session expired')
    return redirect('Frontend_User:login')
