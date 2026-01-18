from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    #authentication
    path('login', login.as_view(), name = 'login'),
    path('logout', logout.as_view(), name = 'logout'),
    path('changepassword', ChangePassword.as_view(), name = 'changepassword'),
    path('forgetpasswordmail', forgetpasswordmail.as_view(), name = 'forgetpasswordmail'),
    path('setnewpassword', setnewpassword.as_view(), name = 'setnewpassword'),
    path('resetpassword', resetpassword.as_view(), name = 'resetpassword'),

    #role
    path('role_list_pagination_api', role_list_pagination_api.as_view(), name = 'role_list_pagination_api'),
    path('rolelist', rolelist.as_view(), name = 'rolelist'),
    path('addrole', addrole.as_view(), name = 'addrole'),
    path('roleupdate', roleupdate.as_view(), name = 'roleupdate'),
    path('roledelete', roledelete.as_view(), name = 'roledelete'),
    path('rolebyid', rolebyid.as_view(), name = 'rolebyid'),


    #menu
    path('menu-list',Menulist.as_view()),
    path('data-permission',GetPermissionData.as_view()),
    path('User-data-permission',GetUserPermissionData.as_view()),
    

    #user
    path('createuser', createuser.as_view(), name = 'createuser'),
    path('user_list_pagination_api', user_list_pagination_api.as_view(), name = 'user_list_pagination_api'),
    path('userlist', userlist.as_view(), name = 'userlist'),
    path('userupdate', userupdate.as_view(), name = 'userupdate'),
    path('userdelete', userdelete.as_view(), name = 'userdelete'),

    path('userdeleteundo', userdeleteundo.as_view(), name = 'userdeleteundo'),
    path('userbyid', userbyid.as_view(), name = 'userbyid'),
    path('check_email_availablity', check_email_availablity.as_view(), name = 'check_email_availablity'),
    path('send_verification_otp_mail', send_verification_otp_mail.as_view(), name = 'send_verification_otp_mail'),
    path('ValidateOTP', ValidateOTP.as_view(), name = 'ValidateOTP'),
    path('register_new_consumer', register_new_consumer.as_view(), name = 'register_new_consumer'),
    
    

    path('customer_list', customer_list.as_view(), name = 'customer_list'),

    path('add_new_customer', add_new_customer.as_view()),



]