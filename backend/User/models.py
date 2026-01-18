from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from helpers.models import TrackingModel
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
import uuid
import jwt
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE



class Role(TrackingModel):
    RoleName = models.CharField(max_length=150)
    
    def __str__(self):
        return self.RoleName

class UserManager(BaseUserManager):
    def create(self,email,password,**extra_fields):
        if not email:
            raise ValueError("User must have a valid email")
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Username = models.CharField(max_length=255,null=True,blank=True)
    textPassword = models.CharField(max_length=255,null=True,blank=True)
    mobileNumber = models.BigIntegerField(null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE,null=True,blank=True)
    source = models.CharField(max_length=255,null=True,blank=True)
    status = models.BooleanField(default=True,null=True,blank=True)
    profile_picture = models.FileField(upload_to='users/profile_picture/', blank=True, null=True,verbose_name='profile_picture Image')
    


    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class UserToken(TrackingModel):
    User = models.CharField(max_length=255,null=True, blank=True)
    source = models.CharField(max_length=255,null=True,blank=True)
    WebToken = models.TextField(null=True, blank=True)
    MobileToken = models.TextField(null=True, blank=True)

class Menu(models.Model):
    isActive=models.BooleanField(default=True)
    menuItem=models.CharField(max_length=255)
    menuPath=models.CharField(max_length=255)
    parentId=models.IntegerField(null=True, blank=True)
    subparentId=models.IntegerField(default=0)
    sortOrder=models.IntegerField(null=True, blank=True)
    isshown = models.BooleanField(default=True)

class RolePermissions(TrackingModel):
    role = models.IntegerField(null=True, blank=True)  
    add = models.BooleanField(default=False)
    view = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    menu= models.IntegerField(default=0)


class UserPermissions(TrackingModel):
    userid = models.CharField(max_length=255)
    role = models.IntegerField(null=True, blank=True)  
    add = models.BooleanField(default=False)
    view = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    menu= models.IntegerField(default=0)


class EmailOTPVerification(TrackingModel):
    email = models.CharField(max_length=255,null=True, blank=True)
    otp = models.CharField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)  
    
    
    
class Customer(TrackingModel):
    name = models.CharField(max_length=255)
    address = models.TextField()
    gstin = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name
