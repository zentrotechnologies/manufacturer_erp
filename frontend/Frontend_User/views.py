from django.shortcuts import render, redirect, HttpResponse,HttpResponseRedirect
import requests
import os
import json
from datetime import datetime,date,timedelta
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import datetime
from datetime import date
# from project.views import statuscheck
from rest_framework.response import Response
from helpers.validations import hosturl
from django.http import JsonResponse


# from Users.context_processers import ImageURL as imageURL
login_url=hosturl+"/api/User/login"
logout_url=hosturl+"/api/User/logout"
forgot_password_url=hosturl+"/api/User/forgetpasswordmail"
get_parent_services_list_url=hosturl+"/api/Services/parentservicelist"
get_child_services_list_url=hosturl+"/api/Services/childservicelist"
add_service_provider_url=hosturl+"/api/User/create_new_service_provider"
get_service_provider_details_url=hosturl+"/api/User/get_service_provider_details"
edit_service_provider_url=hosturl+"/api/User/update_service_provider_basic_details"

# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        data = {}
        data['email'] = email
        data['password'] = password
        data['source'] = 'Mobile'

        login_request = requests.post(login_url, data=data)
        login_response = login_request.json()
        print("login_response",login_response)
        if login_response['response']['n'] == 1:
            token = login_response['data']['token']
            request.session['token'] = token 
            request.session['role_id'] = login_response['data']['role'] 
            request.session['role_name'] = login_response['data']['role_name']  
            request.session['user_name'] = login_response['data']['username']   
            return HttpResponse(json.dumps(login_response),content_type='application/json')
        else:
            # messages.error(request, login_response['response']['msg'])
            return HttpResponse(json.dumps(login_response),content_type='application/json')
    else:
        return render(request, 'Authentication/auth_login_basic.html',)

def logout(request):
    if request.method == 'POST':
        token = request.session.get('token')
        headers = {'Authorization': f'Bearer {token}'}
        logout_request = requests.post(logout_url,headers=headers)
        logout_response = logout_request.json()
        if logout_response['response']['n'] == 1:
            del request.session['token']
            return HttpResponse(json.dumps(logout_response),content_type='application/json')
        else:
            return HttpResponse(json.dumps(logout_response),content_type='application/json')
    else:
        return render(request, 'Authentication/auth_login_basic.html')

def users_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Users/users_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        data = {}
        data['email'] = email
        data['source'] = 'Mobile'

        forgot_password_request = requests.post(forgot_password_url, data=data)
        forgot_password_response = forgot_password_request.json()

        if forgot_password_response['response']['n'] == 1:
 
            return HttpResponse(json.dumps(forgot_password_response),content_type='application/json')
        else:
            # messages.error(request, forgot_password_response['response']['msg'])
            return HttpResponse(json.dumps(forgot_password_response),content_type='application/json')
    else:
        return render(request, 'Authentication/auth_forgot_password_basic.html')





def users_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Users/users_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    

def privacy_policy(request):


    return render(request, 'info/privacy-policy.html')

def terms_and_conditions(request):
    return render(request, 'info/terms-and-conditions.html')

@csrf_exempt
def test_logger(request):
    PaymentTransactionErrorLog.objects.create(error="Webhook test OK")
    return JsonResponse({"status": "logged"})


@csrf_exempt
def mips_imn_redirect(request):
    """
    This view handles redirect after payment success/failure from MIPS.
    It’s usually a GET request — not a webhook.
    """
    try:
        # You can optionally display a simple success/failure message here.
        status = request.GET.get("status", "")
        order_id = request.GET.get("order_id", "")
        transaction_id = request.GET.get("transaction_id", "")
        
        # Option 1: Show a simple success/failure page
        return render(request, "PaymentHostory/payment_result.html", {
            "status": status,
            "order_id": order_id,
            "transaction_id": transaction_id,
        })

        # Option 2 (alternative): redirect user to your frontend success page
        # return redirect(f"https://yourfrontend.com/payment?status={status}&order_id={order_id}")
        
    except Exception as e:
        print("Redirect Error:", e)
        return render(request, "PaymentHistory/payment_result.html", {"status": "error"})




