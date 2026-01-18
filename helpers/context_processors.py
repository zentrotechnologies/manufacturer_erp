import requests
from helpers.validations import hosturl

def get_session(request):
    token = request.session.get('token')
    role_id = request.session.get('role_id')
    role_name = request.session.get('role_name')
    user_name = request.session.get('user_name')

    # Designation = request.session.get('Designation')
    # userID = request.session.get('userID')
    # userEmployeeId=request.session.get('userEmployeeId')
    # rules = request.session.get('rules')
    # roleID = request.session.get('roleID')
    # rolename = request.session.get('rolename')
    
    # companylogo = request.session.get('companylogo')
    # userphoto = request.session.get('userPhoto')
    # is_staff = request.session.get('is_staff')
    


   
    return {'token':token,
            'hosturl':hosturl,
            'role_id':role_id,
            'role_name':role_name,
            'user_name':user_name,
        
            }
