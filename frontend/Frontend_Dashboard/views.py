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
# from project.views import statuscheck




# from Users.context_processers import ImageURL as imageURL
login_url=hosturl+"api/User/login"
# Create your views here.
def home(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Dashboard/dashboard_analytics.html')
    else:

        messages.error(request, 'Session expired. Please log in again.')

        # return render(request, 'Authentication/auth_login_basic.html')
        return redirect('Frontend_User:login') # change this.
