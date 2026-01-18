from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v

# from django.conf.urls import url
urlpatterns = [
    # path('accessDenied',v.accessDenied, name='accessDenied'),
    # path('admin/', admin.site.urls),
    path('', v.login, name='login'),
    path('logout', v.logout, name='logout'),
    path('forgot_password', v.forgot_password, name='forgot_password'),



    path('users_list', v.users_list, name='users_list'),
    path('privacy_policy', v.privacy_policy, name='privacy_policy'),
    path('terms_and_conditions', v.terms_and_conditions, name='terms_and_conditions'),
    path("mips/test_logger/", v.test_logger, name="test_logger"),
    path("mips/imn_redirect/", v.mips_imn_redirect, name="mips_imn_redirect"),  # ✅ add this line

]