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
from django.utils.safestring import mark_safe




# from Users.context_processers import ImageURL as imageURL
add_vendor_url = hosturl + "/api/Masters/add_new_vendor"
edit_vendor_url = hosturl + "/api/Masters/update_vendor"
get_vendor_url = hosturl + "/api/Masters/get_vendor_by_id"
get_vendor_list_url = hosturl + "/api/Masters/vendor_list"


add_raw_material_url = hosturl + "/api/Masters/add_new_raw_material"
edit_raw_material_url = hosturl + "/api/Masters/update_raw_material"
get_raw_material_url = hosturl + "/api/Masters/get_raw_material_by_id"
get_raw_material_list_url = hosturl + "/api/Masters/raw_material_list"

add_machine_url = hosturl + "/api/Masters/add_new_machine"
edit_machine_url = hosturl + "/api/Masters/update_machine"
get_machine_url = hosturl + "/api/Masters/get_machine_by_id"
get_machine_list_url = hosturl + "/api/Masters/machine_list"


add_mould_url = hosturl + "/api/Masters/add_new_mould"
edit_mould_url = hosturl + "/api/Masters/update_mould"
get_mould_url = hosturl + "/api/Masters/get_mould_by_id"
get_mould_list_url = hosturl + "/api/Masters/mould_list"

add_product_url = hosturl + "/api/Masters/add_new_product"
edit_product_url = hosturl + "/api/Masters/update_product"
get_product_url = hosturl + "/api/Masters/get_product_by_id"
get_product_list_url = hosturl + "/api/Masters/product_list"

# Create your views here.
def vendor(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Masters/vendor/vendor-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    
def vendor_list(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/vendor/vendor-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
      
def add_vendor(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()
            add_vendor_request = requests.post(
                add_vendor_url,
                data=data,
                headers=headers
            )
            add_vendor_response = add_vendor_request.json()
            return HttpResponse(
                json.dumps(add_vendor_response),
                content_type='application/json'
            )
        else:
            return render(request, 'Masters/vendor/add-vendor.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def edit_vendor(request, id):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()
            edit_vendor_request = requests.post(
                edit_vendor_url,
                data=data,
                headers=headers
            )
            edit_vendor_response = edit_vendor_request.json()
            return HttpResponse(
                json.dumps(edit_vendor_response),
                content_type='application/json'
            )
        else:
            data = {'id': id}
            get_vendor_request = requests.post(
                get_vendor_url,
                data=data,
                headers=headers
            )
            get_vendor_response = get_vendor_request.json()

            return render(
                request,
                'Masters/vendor/edit-vendor.html',
                {'vendor': get_vendor_response['data']}
            )
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')


def raw_material(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/raw_material/raw-material-list.html')
    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')
def add_raw_material(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            r = requests.post(add_raw_material_url, data=request.POST, headers=headers)
            return HttpResponse(json.dumps(r.json()), content_type='application/json')
        v = requests.post(get_vendor_list_url, data=request.POST, headers=headers)
        v_response=v.json()
        return render(request, 'Masters/raw_material/add-raw-material.html',{'vendors':v_response['data']})
    return redirect('Frontend_User:login')
def edit_raw_material(request, id):
    token = request.session.get('token', False)
    headers = {'Authorization': f'Bearer {token}'}

    if request.method == 'POST':
        r = requests.post(edit_raw_material_url, data=request.POST, headers=headers)
        return HttpResponse(json.dumps(r.json()), content_type='application/json')

    r = requests.post(get_raw_material_url, data={'id': id}, headers=headers)
    v = requests.post(get_vendor_list_url, data=request.POST, headers=headers)
    return render(
        request,
        'Masters/raw_material/edit-raw-material.html',
        {'raw_material': r.json()['data'],'vendors': v.json()['data']}
    )




def machine(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/machine/machine-list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')
      
def add_machine(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()
            add_machine_request = requests.post(
                add_machine_url,
                data=data,
                headers=headers
            )
            add_machine_response = add_machine_request.json()
            return HttpResponse(
                json.dumps(add_machine_response),
                content_type='application/json'
            )
        else:
            return render(request, 'Masters/machine/add-machine.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def edit_machine(request, id):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()
            edit_machine_request = requests.post(
                edit_machine_url,
                data=data,
                headers=headers
            )
            edit_machine_response = edit_machine_request.json()
            return HttpResponse(
                json.dumps(edit_machine_response),
                content_type='application/json'
            )
        else:
            data = {'id': id}
            get_machine_request = requests.post(
                get_machine_url,
                data=data,
                headers=headers
            )
            get_machine_response = get_machine_request.json()

            return render(
                request,
                'Masters/machine/edit-machine.html',
                {'machine': get_machine_response['data']}
            )
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login')

def mould(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/mould/mould-list.html')
    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')
def add_mould(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()
            r = requests.post(add_mould_url, data=data, headers=headers)
            return HttpResponse(json.dumps(r.json()), content_type='application/json')

        m= requests.post(get_machine_list_url, headers=headers)
        return render(
            request,
            'Masters/mould/add-mould.html',
            {'machines': m.json()['data']}
        )

    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')
def edit_mould(request, id):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()
            r = requests.post(edit_mould_url, data=data, headers=headers)
            return HttpResponse(json.dumps(r.json()), content_type='application/json')

        r = requests.post(get_mould_url, data={'id': id}, headers=headers)
        mould_data = r.json().get('data')

        m= requests.post(get_machine_list_url, headers=headers)

        return render(
            request,
            'Masters/mould/edit-mould.html',
            {
                'mould': mould_data,
                'machines': m.json()['data']
            }
        )

    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')


def product(request):
    token = request.session.get('token', False)
    if token:
        return render(request, 'Masters/product/product-list.html')
    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')


def add_product(request):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            # raw_materials[] should be sent as JSON string from frontend
            if 'raw_materials' in data:
                data['raw_materials'] = json.loads(data.get('raw_materials'))

            r = requests.post(add_product_url, json=data, headers=headers)
            return HttpResponse(
                json.dumps(r.json()),
                content_type='application/json'
            )

        m = requests.post(get_mould_list_url, json={}, headers=headers)
        r = requests.post(get_raw_material_list_url, json={}, headers=headers)

        return render(
            request,
            'Masters/product/add-product.html',
            {
                'moulds': m.json()['data'],
                'raw_materials': r.json()['data'],
            }
        )

    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')
def edit_product(request, id):
    token = request.session.get('token', False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':
            data = request.POST.copy()

            # DO NOT json.loads here
            # Send raw_materials as string (FormData style)
            r = requests.post(
                edit_product_url,
                data=data,              # ✅ FIX
                headers=headers
            )

            try:
                response = r.json()
            except ValueError:
                return HttpResponse(
                    json.dumps({
                        "data": [],
                        "response": {
                            "n": 0,
                            "msg": "Server error while updating product",
                            "status": "error"
                        }
                    }),
                    content_type='application/json'
                )

            return HttpResponse(
                json.dumps(response),
                content_type='application/json'
            )

        # ---------- GET (Edit Page) ----------
        r = requests.post(
            get_product_url,
            data={'id': id},
            headers=headers
        )
        response = r.json()

        m = requests.post(get_mould_list_url, data={}, headers=headers)
        rm = requests.post(get_raw_material_list_url, data={}, headers=headers)

        return render(
            request,
            'Masters/product/edit-product.html',
            {
                'product': response['data']['product'],
                'product_raw_materials': response['data']['raw_materials'],
                'moulds': m.json().get('data', []),
                'raw_materials': rm.json().get('data', []),
            }
        )

    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')
    


def batch(request):
    token = request.session.get('token', False)

    if token:
        return render(
            request,
            'Masters/batch/batch-list.html'
        )

    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')


def add_batch(request):

    token = request.session.get('token', False)

    if token:

        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':

            data = request.POST.copy()

            r = requests.post(
                hosturl + "/api/Production/add_new_batch",
                data=data,
                headers=headers
            )

            return HttpResponse(
                json.dumps(r.json()),
                content_type='application/json'
            )

        # GET → Load Product dropdown
        p = requests.post(
            get_product_list_url,
            data={},
            headers=headers
        )
        rm = requests.post(get_raw_material_list_url, data={}, headers=headers)

        return render(
            request,
            'Masters/batch/add-batch.html',
            {
                'products': p.json().get('data', []),
                'raw_materials': mark_safe(json.dumps(rm.json().get('data', []))),


            }
        )

    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')

def edit_batch(request, id):

    token = request.session.get('token', False)

    if token:

        headers = {'Authorization': f'Bearer {token}'}

        if request.method == 'POST':

            data = request.POST.copy()

            r = requests.post(
                hosturl + "/api/Production/update_batch",
                data=data,
                headers=headers
            )

            return HttpResponse(
                json.dumps(r.json()),
                content_type='application/json'
            )

        # ---------- GET (Edit Page) ----------

        r = requests.post(
            hosturl + "/api/Production/get_batch_by_id",
            data={'id': id},
            headers=headers
        )

        response = r.json()

        p = requests.post(
            get_product_list_url,
            data={},
            headers=headers
        )
        rm = requests.post(get_raw_material_list_url, data={}, headers=headers)

        return render(
            request,
            'Masters/batch/edit-batch.html',
            {
                'batch': response.get('data'),
                'products': p.json().get('data', []),
                'raw_materials': mark_safe(json.dumps(rm.json().get('data', []))),
                'existing_rm': mark_safe(json.dumps(response.get('data', {}).get('raw_materials', [])))
            }
        )


    messages.error(request, 'Session expired. Please log in again.')
    return redirect('Frontend_User:login')

def delete_batch(request):

    token = request.session.get('token', False)

    if token:

        headers = {'Authorization': f'Bearer {token}'}

        r = requests.post(
            hosturl + "/api/Production/delete_batch",
            data=request.POST,
            headers=headers
        )

        return HttpResponse(
            json.dumps(r.json()),
            content_type='application/json'
        )

    return HttpResponse(
        json.dumps({
            "data": [],
            "response": {
                "n": 0,
                "msg": "Session expired",
                "status": "error"
            }
        }),
        content_type='application/json'
    )