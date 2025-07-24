"""
URL patterns for SCD app
"""

from django.urls import path
from . import views

app_name = 'scd_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('demo/', views.demo_queries, name='demo'),
    path('jobs/', views.jobs_list, name='jobs'),
    path('jobs/company/<str:company_id>/', views.jobs_by_company, name='jobs_by_company'),
    path('jobs/contractor/<str:contractor_id>/', views.jobs_by_contractor, name='jobs_by_contractor'),
    path('timelogs/contractor/<str:contractor_id>/', views.timelogs_by_contractor, name='timelogs_by_contractor'),
    path('payments/contractor/<str:contractor_id>/', views.payments_by_contractor, name='payments_by_contractor'),
    path('dashboard/contractor/<str:contractor_id>/', views.contractor_dashboard, name='contractor_dashboard'),
    path('report/company/<str:company_id>/', views.company_report, name='company_report'),
] 