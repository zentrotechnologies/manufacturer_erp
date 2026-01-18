from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    path('add-production-entry',v.add_production_entry,name='add_production_entry'),
    path('production-list', v.production_list, name='production_list'),
    path('view-production/<int:id>', v.view_production, name='view_production'),
    path('daily-production-report',v.daily_production_report,name='daily_production_report')

]
