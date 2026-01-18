
from .models import *
from rest_framework import serializers
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields='__all__'

class UserlistSerializer(serializers.ModelSerializer):
    role =  serializers.StringRelatedField()
    class Meta:
        model= User
        fields=['id','Username','mobileNumber','email','role']

class CustomUserSerializer(serializers.ModelSerializer):


    Role_name = serializers.SerializerMethodField()
    def get_Role_name(self, obj):
        obj_id = obj.role_id
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Role.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.RoleName
                else:
                    return None
            except Role.DoesNotExist:
                return None
        return None
    
    


    short_name = serializers.SerializerMethodField()
    def get_short_name(self, obj):
        Username = obj.Username
        if Username is not None and Username !='' and Username !='None':

            #convert user name to short Initials 
            name_parts = Username.split()
            
            # Get initials from each part (handle cases with multiple spaces)
            initials = [part[0].upper() for part in name_parts if part]
            
            # Join the initials (take first 2 if name has many parts)
            shortname = ''.join(initials[:2]) if len(initials) > 1 else initials[0] if initials else ''
            return shortname
        else:

            return 'NA'
    
    class Meta:
        model= User
        fields='__all__'


class Roleserializer(serializers.ModelSerializer):
    class Meta:
        model= Role
        fields='__all__'


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields ="__all__"


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermissions
        fields = "__all__"


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissions
        fields = "__all__"



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Customer
        fields='__all__'



        