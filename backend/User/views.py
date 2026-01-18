from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from .jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from manufacturer_erp.settings import EMAIL_HOST_USER
from django.contrib.auth.hashers import make_password,check_password
from .common import CustomPagination
import re
import random
from django.core.mail import send_mail
from django.utils.timezone import make_aware
from django.utils import timezone
from django.db.models import F, FloatField, ExpressionWrapper,Q
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt
import math
from helpers.validations import hosturl
from helpers.custom_functions import *
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives




def createtoken(uuid,email,source):
    token = jwt.encode(
        {'id': uuid,
            'email': email,
            'source':source
           },
        settings.SECRET_KEY, algorithm='HS256')
    return token

class login(GenericAPIView):
    def post(self,request):
        email = request.data.get("email")
        Password = request.data.get("password")
        source = request.data.get("source")
        if email is None or Password is None :
            return Response( {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'Please provide email and password',
                    'n':0
                    }})
        
        userexist = User.objects.filter(email=email, isActive=True).first()
        if userexist is None:
           return Response(
                    {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'This user is not found',
                    'n':0
                    }}
                           )
        elif userexist.status == False:
            return Response(
                    {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'This account is deactivated',
                    'n':0
                    }}
                           )
        else:
            user_serializer=UserSerializer(userexist)
            p = check_password(Password,userexist.password)
            if p is False:
                return Response({
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'Please enter correct password',
                    'n':0
                    }})
            else:
                useruuid = str(userexist.id)
                username = userexist.Username
                # short_name = ''.join([word[0] for word in username.split()]).upper()

                role =  userexist.role_id
                role_name =  str(userexist.role)
                ifservice_provider=False
                service_provider_details={}



                



                print("userexist.role",userexist.role)
                
                Token = createtoken(useruuid,email,source)
                
                if source == "Web":
                    web_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createwebtoken = UserToken.objects.create(User=useruuid,WebToken=Token,source=source)
                elif source == "Mobile":
                    mobile_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createmobiletoken = UserToken.objects.create(User=useruuid,MobileToken=Token,source=source)
                else:
                    return Response({
                    "data" : {'token':'','username':'','short_name':'','user_id':'','role':'','role_name':'','Menu':[],'ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'Please Provide Source',
                    'n':0
                    }
                })
                
                return Response({
                    "data" : {'token':Token,'username':username,'short_name':'','user_id':useruuid,'role':role,'role_name':role_name,'ifservice_provider':ifservice_provider,'email':email,'service_provider_details':service_provider_details},
                    "response":{
                    "n": 1 ,
                    "msg" : "Login successful",
                    "status":"success"
                    }
                })
            
class logout(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
      
        auth_header = get_authorization_header(request)
        auth_data = auth_header.decode('utf-8')
        auth_token = auth_data.split(" ")
        token = auth_token[1]
        mobiletoken = UserToken.objects.filter(MobileToken=token,isActive=True).update(isActive=False)
        webtoken = UserToken.objects.filter(WebToken=token,isActive=True).update(isActive=False)
        return Response({
                        "data" : '',
                        "response":{
                        "n": 1 ,
                        "msg" : "Logout successful",
                        "status":"success"
                        }
                    })

class ChangePassword(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        id = request.user.id
        if id is not None:
            userObject = User.objects.filter(id=id,isActive=True,status=True).first()
        
            if userObject:
                password = request.data.get('oldpassword')
                currentPassword = check_password(password,userObject.password)
                if currentPassword==True:
                    newpassword = request.data.get('newpassword')
                
                    confirmpassword = request.data.get('confirmpassword')
                
                    if newpassword==confirmpassword:
                        data['password']= make_password(newpassword)
                        data['textPassword'] = newpassword
                        userSerializer = UserSerializer(userObject,data=data,partial=True)
                        if userSerializer.is_valid():
                            userSerializer.save()

                            tokenfalse = UserToken.objects.filter(User=id,isActive=True).update(isActive=False)
                           
                            return Response({"data":'',"response": {"n": 1, "msg": "Password updated successfully","status": "success"}})
                        else:
                            return Response({"data":'',"response": {"n": 0, "msg": "Password not updated ","status": "error"}})
                    else:
                        return Response({"data":'',"response": {"n": 0, "msg": "New and confirm password not matched ","status": "error"}})
                else:
                    return Response({"data":'',"response": {"n": 0, "msg": "Old password is wrong","status": "error"}})

        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Couldnt find id","status": "error"}})

class forgetpasswordmail(GenericAPIView):
    def post(self,request):
        data={}
        data['email']=request.data.get('email')
        print("request.data",request.data)
        userdata = User.objects.filter(email=data['email'],isActive=True,status=True).first()
        if userdata is not None:
            email =   data['email']
            data2 = {'user_id':userdata.id,'user_email':userdata.email,'frontend_url':hosturl}
            html_mail = render_to_string('mails/reset_password.html',data2)
            
            mailMsg = EmailMessage(
                'Forgot Password?',
                 html_mail,
                'no-reply@mozilourislandguide.com',
                [email],
                )
            mailMsg.content_subtype ="html"
            mailsend = mailMsg.send()
           
            return Response({"data":{},"response":{"n": 1,"msg":"Email Sent Successfully!", "status":"success" }})
        else:
            return Response({"data":{},"response":{"n": 0,"msg" : "User not found", "status":"error"}})



class setnewpassword(GenericAPIView):
    def post(self,request):
        data={}
        data['email']=request.data.get('email')
        empdata = User.objects.filter(email=data['email'],isActive=True,status=True).first()
        if empdata is not None:
            data['Password']=request.data.get('Password')
            data['cfpassword']=request.data.get('cfpassword')
            userpassword = data['Password']
            if data['Password'] != data['cfpassword']:
                return Response({"data":{},"response":{"n": 0 ,"msg":"Passwords do not match","status":"passwords do not match"}})
            else:
                data['password']=make_password(userpassword)
                data['textPassword'] = userpassword
                data['PasswordSet'] = True
                serializer = UserSerializer(empdata,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data" : serializer.data,"response":{"n":1,"msg":"Password set Successfully!","status":"success"}})
                else:

                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

        else:
            return Response({ "data":{},"response":{"n":0,"msg":"User not found", "status":"error"}})

class resetpassword(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        data['id']=request.data.get('id')
        empdata = User.objects.filter(id=data['id'],isActive=True,PasswordSet=True,status=True).first()
        if empdata is not None:
            data['Password']=request.data.get('Password')
            data['cfpassword']=request.data.get('cfpassword')
            userpassword = data['Password']
            if data['Password'] != data['cfpassword']:
                return Response({"data":{},"response":{"n": 0 ,"msg":"Passwords do not match","status":"passwords do not match"}})
            else:
                data['password']=make_password(userpassword)
                data['textPassword'] = userpassword
                serializer = UserSerializer(empdata,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data" : serializer.data,"response":{"n":1,"msg":"Password Reset Successfully!","status":"success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

        else:
            return Response({ "data":{},"response":{"n":0,"msg":"User not found", "status":"error"}})
        
#role -----------------------------------------------------------------------------------------------------

class addrole(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['RoleName']=request.data.get('RoleName')
        result = []
        
        if data['RoleName'] is None or data['RoleName'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide Role name", "status":"error"}})
        
        
        # request_data['createdBy'] = request.session.get('user_id')
        if 'result' in request_data.keys():
            result = request_data['result']
        roleexist = Role.objects.filter(RoleName=data['RoleName'],isActive=True).first()
        if roleexist is None:
            serializer = Roleserializer(data=data)
            if serializer.is_valid():
                serializer.save()
                for i in result:
                    RolePermissions.objects.create(
                        role = serializer.data['id'],
                        add = i['create'],
                        view = i['read'],
                        edit = i['edit'],
                        delete = i['delete'],
                        menu= i['menu_id']
                    )
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"Role added Successfully!","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"Role already exist", "status":"error"}})

class rolelist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        role_objs = Role.objects.filter(isActive=True).order_by('id')
        serializer = Roleserializer(role_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Roles found Successfully",
                "status":"success"
                }
        })
    
class role_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def get(self,request):
        RoleMaster_objs = Role.objects.filter(isActive=True).order_by('id')
        page4 = self.paginate_queryset(RoleMaster_objs)
        serializer = Roleserializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class roleupdate(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('roleid')
        result = []
        if 'result' in request.data.keys():
            result = json.loads(request.data.get('result'))
        roleexist = Role.objects.filter(id=id,isActive= True).first()
        if roleexist is not None:
            data['RoleName']=request.data.get('RoleName')
            # data['updatedBy'] =str(request.user.id)
            if data['RoleName'] is None or data['RoleName'] =='':
                return Response({ "data":{},"response":{"n":0,"msg":"Please provide Role name", "status":"error"}})
        
            roleindata = Role.objects.filter(RoleName=data['RoleName'],isActive= True).exclude(id=id).first()
            if roleindata is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "Role already exist","status": "error"}})
            else:
                serializer = Roleserializer(roleexist,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    RolePermissions.objects.filter(role=serializer.data['id']).delete()
                    for i in result:
                        RolePermissions.objects.create(
                            role = serializer.data['id'],
                            add = i['create'],
                            view = i['read'],
                            edit = i['edit'],
                            delete = i['delete'],
                            menu= i['menu_id']
                        )
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "Role updated successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role not found ","status": "error"}})

class rolebyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        id = request.data.get('roleid')
        roleobjects = Role.objects.filter(id=id,isActive=True).first()
        if roleobjects is not None:
            serializer = Roleserializer(roleobjects)
            permission_object = RolePermissions.objects.filter(role= id).order_by("menu")
            permission_ser = PermissionsSerializer(permission_object,many=True)

            serializer_data = serializer.data
            serializer_data.update({
                "permissions":permission_ser.data
            })
            return Response({"data":serializer_data,"response": {"n": 1, "msg": "Role data shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role data not found  ","status": "success"}})

class roledelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('roleid')
        existrole = Role.objects.filter(id=id,isActive=True).first()
        if existrole is not None:
            data['isActive'] = False
            serializer = Roleserializer(existrole,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Role deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role Not Found","status": "error"}})

#user----------------------------------------------------------------------------------------------------

class createuser(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['Username']=request.data.get('Username')
        if data['Username'] is None or data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user name", "status":"error"}})
        
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})
        
        data['mobileNumber']=request.data.get('mobileNumber')
        if data['mobileNumber'] is None or data['mobileNumber'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})
        
        data['email']=request.data.get('email')
        data['role'] = request.data.get('role')
        data['password'] = data['textPassword']
        data['isActive'] = True
        result = []
        if 'result' in request.data.keys():
            result = request.data.get('result')

        roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
        if roleobj is not None:
            rolename = roleobj.RoleName
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "status": "error"}})

        emailobj = User.objects.filter(isActive=True, email=data['email']).first()
        mobileobj = User.objects.filter(isActive=True, mobileNumber=data['mobileNumber']).first()        
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        elif mobileobj is not None:        
            return Response({"data":'',"response": {"n": 0, "msg": "Mobile already exist", "status": "error"}})
        
        else:
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                userid = serializer.data['id']

                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User registered successfully","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        
class userlist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        empobjects = User.objects.filter(isActive=True).order_by('id')
        serializer = CustomUserSerializer(empobjects, many=True)
        return Response({"data":serializer.data,"response": {"n": 1, "msg": "User list shown successfully","status": "success"}})

class user_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):
        searchtext = request.data.get("searchtext")
        if searchtext is not None and searchtext != '':
            UserMaster_objs = User.objects.filter(Q(Username__icontains=searchtext,isActive=True)| Q(mobileNumber__icontains =searchtext,isActive=True)).order_by('Username')
        else:
            UserMaster_objs = User.objects.filter(isActive=True).order_by('Username')
        activation_status=request.data.get('activation_status')
        if activation_status is not None and activation_status !='':
            if activation_status == 'true':

                UserMaster_objs = UserMaster_objs.filter(status=True)
            elif activation_status == 'false':

                UserMaster_objs = UserMaster_objs.filter(status=False)     



        page4 = self.paginate_queryset(UserMaster_objs)
        serializer = CustomUserSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)

class userbyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        userID = request.data.get("userID")
        empobjects = User.objects.filter(id=userID,isActive=True).first()
        if empobjects is not None:
            serializer = UserSerializer(empobjects)
            serializer_data = serializer.data
            userpermissionobj = UserPermissions.objects.filter(userid=str(userID))
            userser = UserPermissionSerializer(userpermissionobj,many=True)
            serializer_data.update({
                'permissions' : userser.data
            })
            return Response({"data":serializer_data,"response": {"n": 1, "msg": "User shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found  ","status": "success"}})


class userupdate(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userid = request.data.get('userid')
        data['userid'] = request.data.get('userid')
        existemp = User.objects.filter(id=userid,isActive=True).first()
        if existemp is not None:
            data['Username']=request.data.get('Username')
            data['mobileNumber']=request.data.get('mobileNumber')
            mobileNumber = data['mobileNumber']
            data['email']=request.data.get('email')
            email = data['email']
            data['role'] = request.data.get('role')
            data['isActive'] = True
            result = []
            if 'result' in request.data.keys():
                result = json.loads(request.data.get('result'))
            # data['updatedBy'] = str(request.user.id)

            roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
            if roleobj is not None:
                rolename = roleobj.RoleName

            else:
                return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "status": "error"}})
            serializer = UserSerializer(existemp,data=data,partial=True)
            emailObject = User.objects.filter(email__in = [email.strip().capitalize(),email.strip(),email.title()],isActive__in=[True]).exclude(id=userid).first()
            mobObject = User.objects.filter(mobileNumber = mobileNumber,isActive__in=[True]).exclude(id=userid).first()
            if emailObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this email id already exist","status": "error"}})
            elif mobObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this mobile number already exist","status": "error"}})
            else:
                if serializer.is_valid():
                    serializer.save()
                    userperm = UserPermissions.objects.filter(userid=data['userid']).delete()
                    for i in result:
                        UserPermissions.objects.create(
                            userid = data['userid'],
                            role =  data['role'],
                            add = i['create'],
                            view = i['read'],
                            edit = i['edit'],
                            delete = i['delete'],
                            menu= i['menu_id']
                        )
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "User updated successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})

class userdelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = request.data.get('userID')
        existemp = User.objects.filter(id=userID,isActive=True).first()
        if existemp is not None:
            data['isActive'] = False
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})

class userdeleteundo(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = request.data.get('userID')
        existemp = User.objects.filter(id=userID,isActive=False).first()
        if existemp is not None:
            data['isActive'] = True
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User retrived successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})
                
#menu-----------------------------------------------------------------------------------------------
class Menulist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        menuobj=Menu.objects.filter(isActive=True).order_by('sortOrder')
        serializer = MenuSerializer(menuobj,many=True)
        response_={
            'status':'success',
            'msg':'Menu List Found Successfully.',
            'data':serializer.data
        }
        return Response(response_,status=200)
       
class GetPermissionData(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        data['role'] = request.data.get('role')
        roleobj = RolePermissions.objects.filter(role=data['role'], isActive=True).order_by('menu')
        if roleobj is not None:  
            serializer = PermissionsSerializer(roleobj,many=True)
            for i in serializer.data:
                menuobj=Menu.objects.filter(id=i['menu']).first()
                i['menu_path'] = menuobj.menuPath
                i['menu_name'] = menuobj.menuItem
                i['parent_id'] = menuobj.parentId
                i['sub_parent_id'] = menuobj.subparentId
            response_={
                    'status':'success',
                    'msg':'Permission found Successfully.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                'status':'error',
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)

class GetUserPermissionData(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        data['userid'] = request.data.get('userid')
        userobj = UserPermissions.objects.filter(userid=data['userid'], isActive=True).order_by('menu')
        if userobj is not None:  
            serializer = UserPermissionSerializer(userobj,many=True)
            for i in serializer.data:
                menuobj=Menu.objects.filter(id=i['menu']).first()
                i['menu_path'] = menuobj.menuPath
                i['menu_name'] = menuobj.menuItem
                i['parent_id'] = menuobj.parentId
                i['sub_parent_id'] = menuobj.subparentId
                i['isshown'] = menuobj.isshown


            response_={
                    'status':'success',
                    'msg':'User Permissions found Successfully.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                'status':'error',
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)

class getmappingusers(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        cclist = []
        # designlist = []
        # operationlist = []
        # budgetinglist = []
        # planninglist = []
        # Auditorlist = []

        ccuserobjs = User.objects.filter(isActive=True,role__in=Role.objects.filter(RoleName__iexact='GPL Users')).order_by('id')
        if ccuserobjs.exists():
            ccUserser = UserSerializer(ccuserobjs,many=True)

        
        auditobjs = User.objects.filter(isActive=True,role__in=Role.objects.filter(RoleName__iexact='Auditor')).order_by('id')
        if auditobjs.exists():
            auditUserser = UserSerializer(auditobjs,many=True)
            for a in auditUserser.data:
                cclist.append(a)

       


        context = {
            'cclist':cclist,
            # 'designlist':designlist,
            # 'operationlist':operationlist,
            # 'budgetinglist':budgetinglist,
            # 'planninglist':planninglist,
            # 'Auditorlist':Auditorlist
        }
         

        response_={
            'status':'success',
            'msg':'User list found  Successfully.',
            'data':context
        }
        return Response(response_,status=200)
    

























class register_new_consumer(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        
        data['Username']=request.data.get('Username')
        if data['Username'] is None or data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide consumer name", "status":"error"}})
        data['email']=str(request.data.get('email')).lower()
        if data['email'] is None or data['email'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide email id", "status":"error"}})
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})
        
        # data['mobileNumber']=request.data.get('mobileNumber')
        # if data['mobileNumber'] is None or data['mobileNumber'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})

        data['password'] = data['textPassword']
        data['isActive'] = True
        data['role'] = 3

        
        role_objs = Role.objects.filter(isActive=True,id=3).first()
        if role_objs is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Role Not exist", "status": "error"}})        

        emailobj = User.objects.filter(isActive=True, email=data['email']).first()
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        else:
            serializer1 = UserSerializer(data=data)
            if serializer1.is_valid():
                serializer1.save()
                return Response({"data":serializer1.data,"response": {"n": 1, "msg": "Registration successfull", "status": "error"}})        
            else:
                first_key, first_value = next(iter(serializer1.errors.items()))
                return Response({"data" : serializer1.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
    


















class check_email_availablity(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = {}
        email = request.data.get('email', '').strip().lower()
        logined_user_id = str(request.data.get('logined_user_id', ''))
        data['email'] = email

        # Check if email is provided
        if not email:
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Please provide email", "status": "error"}
            })

        # Validate email format using regex
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Please provide valid email format", "status": "error"}
            })

        # Check if email already exists

        print("logined_user_id",logined_user_id)
        email_obj = User.objects.filter(isActive=True, email=email)
        if logined_user_id is not None and logined_user_id !='':
            email_obj=email_obj.exclude(id=logined_user_id).first()
        else:
            email_obj=email_obj.first()





        if email_obj:
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Email already exists, try another email", "status": "error"}
            })
        else:
            return Response({
                "data": {}, 
                "response": {"n": 1, "msg": "Email available", "status": "success"}
            })

class send_verification_otp_mail(GenericAPIView):

    def post(self, request):
        email = request.data.get("email", "").strip().lower()

        # Validate email
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not email or not re.match(email_regex, email):
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Invalid or missing email", "status": "error"}
            },)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save to DB (overwrite if email already exists)
        EmailOTPVerification.objects.update_or_create(
            email=email,
            defaults={
                'otp': otp,
                'created_at': timezone.now()
            }
        )
        html_content = render_to_string('Mails/otp_email_template.html', {'otp': otp})
        msg = EmailMultiAlternatives(
            subject="Your OTP Verification Code",
            body=f"Your OTP code is {otp}. It will expire in 10 minutes.",
            from_email="no-reply@mozilourislandguide.com",
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send(fail_silently=False)
            print("Email sent to", email)
        except Exception as e:
            print("EMAIL SEND ERROR:", e)



        return Response({
            "data": {"email": email}, 
            "response": {"n": 1, "msg": "OTP sent successfully", "status": "success"}
        })

class ValidateOTP(GenericAPIView):
    def post(self, request):
        # Get email and OTP from request data
        email = request.data.get("email", "").strip().lower()
        otp = request.data.get("otp", "").strip()

        # Validate email
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not email or not re.match(email_regex, email):
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Invalid or missing email", "status": "error"}
            })

        # Validate OTP
        if not otp:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "OTP is required", "status": "error"}
            })

        # Fetch the OTP record from the database
        otp_record = EmailOTPVerification.objects.filter(email=email).first()

        if not otp_record:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "No OTP record found for this email", "status": "error"}
            })

        # Check if OTP is expired (Optional: Add expiration time like 10 minutes)
        otp_expiry_time = otp_record.created_at + timedelta(minutes=10)
        print("otp_expiry_time",timezone.now(),otp_expiry_time)
        if timezone.now() > otp_expiry_time:

        # if make_aware(datetime.now()) > otp_expiry_time:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "OTP has expired, please request a new one", "status": "error"}
            })

        # Compare provided OTP with the stored OTP
        if otp == otp_record.otp:
            return Response({
                "data": {},
                "response": {"n": 1, "msg": "OTP validated successfully", "status": "success"}
            })
        else:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Invalid OTP", "status": "error"}
            })



class customer_list(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        customer_obj = Customer.objects.filter(isActive=True).order_by('name')
        serializer = CustomerSerializer(customer_obj, many=True)
        return Response({"data":serializer.data,"response": {"n": 1, "msg": "User list shown successfully","status": "success"}})
    
    
    
    
# Sales/views.py
class add_new_customer(GenericAPIView):

    def post(self, request):
        data = request.data.copy()
        data['state']='27'
        if Customer.objects.filter(name=data.get('name'), isActive=True).exists():
            return Response({
                "data": [],
                "response": {
                    "n": 0,
                    "msg": "Customer already exists",
                    "status": "error"
                }
            })

        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save(isActive=True)
            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Customer added successfully",
                    "status": "success"
                }
            })

        key, val = next(iter(serializer.errors.items()))
        return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": f"{key}: {val[0]}",
                "status": "error"
            }
        })

    
    
    
    
    
    
    