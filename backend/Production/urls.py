from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('create_production_entry', CreateProductionEntryAPI.as_view()),
    path('production_entry_list_pagination_api',ProductionEntryListAPI.as_view()),
    path('get_production_entry_by_id',GetProductionEntryByIdAPI.as_view()),
    path('daily_production_report_api',DailyProductionReportAPI.as_view()),
    path('batch_list',BatchListAPI.as_view()),
    path('export_daily_production_report_excel',export_daily_production_report_excel, name='export_daily_production_report_excel'),




    path('batch_list_pagination_api', batch_list_pagination_api.as_view()),
    path('add_new_batch', add_new_batch.as_view()),
    path('batch_list', batch_list.as_view()),
    path('get_batch_by_id', get_batch_by_id.as_view()),
    path('update_batch', update_batch.as_view()),
    path('delete_batch', delete_batch.as_view()),


]