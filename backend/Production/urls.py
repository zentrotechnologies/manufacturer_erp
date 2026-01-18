from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('create_production_entry', create_production_entry.as_view()),
    path('production_entry_list_pagination_api',production_entry_list_pagination_api.as_view()),
    path('get_production_entry_by_id',get_production_entry_by_id.as_view()),
    path('daily_production_report_api',daily_production_report_api.as_view()),
    path('export_daily_production_report_excel',export_daily_production_report_excel, name='export_daily_production_report_excel'),

]