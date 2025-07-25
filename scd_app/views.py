"""
Django views demonstrating SCD abstraction usage
"""

import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .query_examples import SCDQueryExamples, demonstrate_query_improvements
from .scd_manager import get_latest_jobs, get_latest_timelogs, get_latest_payment_line_items


def index(request):
    """Basic info about the SCD implementation"""
    return JsonResponse({
        'message': 'SCD Work Trial - Django Implementation',
        'description': 'Abstraction layer for Slowly Changing Dimensions',
        'endpoints': [
            '/api/demo/ - Query demonstrations',
            '/api/jobs/ - All latest jobs',
            '/api/jobs/company/<id>/ - Jobs by company',
            '/api/jobs/contractor/<id>/ - Jobs by contractor',
            '/api/timelogs/contractor/<id>/ - Timelogs by contractor',
            '/api/payments/contractor/<id>/ - Payments by contractor',
            '/api/dashboard/contractor/<id>/ - Contractor dashboard',
            '/api/report/company/<id>/ - Company spending report',
        ]
    })


def demo_queries(request):
    """Demonstrate the SCD abstraction with example queries"""
    try:
        # Create examples directly without printing
        examples = SCDQueryExamples()
        company_id = "comp_demo123"
        contractor_id = "cont_demo456"
        
        # Get the query results
        old_jobs = examples.get_active_jobs_for_company_old_way(company_id)
        new_jobs = examples.get_active_jobs_for_company_new_way(company_id)
        
        # Get payment line items
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        payments = examples.get_payment_line_items_for_contractor_optimized(
            contractor_id, start_date, end_date
        )
        
        # Safely get SQL queries
        def get_sql_safe(queryset):
            try:
                return str(queryset.query)
            except Exception:
                return "(empty queryset)"
        
        return JsonResponse({
            'message': 'SCD Query Demonstration',
            'note': 'This shows how the abstraction simplifies complex SCD queries',
            'examples': {
                'old_jobs_sql': get_sql_safe(old_jobs),
                'new_jobs_sql': get_sql_safe(new_jobs),
                'payments_sql': get_sql_safe(payments),
            },
            'benefits': [
                'Simplified query syntax',
                'Automatic latest version filtering',
                'Performance optimization for large datasets',
                'Reduced code duplication',
                'Developer-friendly interface'
            ]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def jobs_list(request):
    """Get all latest version jobs"""
    try:
        # Using the abstraction
        jobs = get_latest_jobs()
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'version': job.version,
                'uid': job.uid,
                'title': job.title,
                'status': job.status,
                'rate': str(job.rate),
                'company_id': job.company_id,
                'contractor_id': job.contractor_id,
                'created_at': job.created_at.isoformat(),
            })
        
        return JsonResponse({
            'jobs': jobs_data,
            'count': len(jobs_data),
            'note': 'All latest versions using SCD abstraction'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def jobs_by_company(request, company_id):
    """
    QUERY PATTERN 1: Get all active Jobs for a company (latest version filtering)
    """
    try:
        status_filter = request.GET.get('status', 'active')
        
        # Using SCD abstraction - simple and clean
        jobs = get_latest_jobs(company_id=company_id, status=status_filter)
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'version': job.version,
                'uid': job.uid,
                'title': job.title,
                'status': job.status,
                'rate': str(job.rate),
                'company_id': job.company_id,
                'contractor_id': job.contractor_id,
                'created_at': job.created_at.isoformat(),
            })
        
        return JsonResponse({
            'company_id': company_id,
            'status_filter': status_filter,
            'jobs': jobs_data,
            'count': len(jobs_data),
            'note': 'Query Pattern 1: Latest jobs for company using SCD abstraction'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def jobs_by_contractor(request, contractor_id):
    """
    QUERY PATTERN 2: Get all active Jobs for a contractor (latest version filtering)
    """
    try:
        status_filter = request.GET.get('status', 'active')
        
        # Using SCD abstraction
        jobs = get_latest_jobs(contractor_id=contractor_id, status=status_filter)
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'version': job.version,
                'uid': job.uid,
                'title': job.title,
                'status': job.status,
                'rate': str(job.rate),
                'company_id': job.company_id,
                'contractor_id': job.contractor_id,
                'created_at': job.created_at.isoformat(),
            })
        
        return JsonResponse({
            'contractor_id': contractor_id,
            'status_filter': status_filter,
            'jobs': jobs_data,
            'count': len(jobs_data),
            'note': 'Query Pattern 2: Latest jobs for contractor using SCD abstraction'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def timelogs_by_contractor(request, contractor_id):
    """
    QUERY PATTERN 4: Get all Timelogs for a contractor in a time period (latest versions only)
    """
    try:
        # Get date range from query params
        days_back = int(request.GET.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        # Use SCD abstraction
        examples = SCDQueryExamples()
        timelogs = examples.get_timelogs_for_contractor_new_way(
            contractor_id, start_timestamp, end_timestamp
        )
        
        timelogs_data = []
        total_duration = 0
        for timelog in timelogs:
            timelogs_data.append({
                'id': timelog.id,
                'version': timelog.version,
                'uid': timelog.uid,
                'duration': timelog.duration,
                'duration_hours': round(timelog.duration / (1000 * 60 * 60), 2),
                'time_start': timelog.time_start,
                'time_end': timelog.time_end,
                'type': timelog.type,
                'job_uid': timelog.job_uid,
                'created_at': timelog.created_at.isoformat(),
            })
            total_duration += timelog.duration
        
        return JsonResponse({
            'contractor_id': contractor_id,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days_back': days_back
            },
            'timelogs': timelogs_data,
            'count': len(timelogs_data),
            'total_hours': round(total_duration / (1000 * 60 * 60), 2),
            'note': 'Query Pattern 4: Latest timelogs for contractor in time period'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def payments_by_contractor(request, contractor_id):
    """
    QUERY PATTERN 3: Get all PaymentLineItems for a contractor in a time period (latest versions only)
    """
    try:
        # Get date range from query params
        days_back = int(request.GET.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Use SCD abstraction
        examples = SCDQueryExamples()
        payments = examples.get_payment_line_items_for_contractor_optimized(
            contractor_id, start_date, end_date
        )
        
        payments_data = []
        total_amount = 0
        for payment in payments:
            payments_data.append({
                'id': payment.id,
                'version': payment.version,
                'uid': payment.uid,
                'amount': str(payment.amount),
                'status': payment.status,
                'job_uid': payment.job_uid,
                'timelog_uid': payment.timelog_uid,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'created_at': payment.created_at.isoformat(),
            })
            total_amount += payment.amount
        
        return JsonResponse({
            'contractor_id': contractor_id,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days_back': days_back
            },
            'payments': payments_data,
            'count': len(payments_data),
            'total_amount': str(total_amount),
            'note': 'Query Pattern 3: Latest payment line items for contractor in time period'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def contractor_dashboard(request, contractor_id):
    """
    Combined dashboard showing all contractor data using SCD abstraction
    """
    try:
        days_back = int(request.GET.get('days', 30))
        
        # Use SCD abstraction for efficient data retrieval
        examples = SCDQueryExamples()
        dashboard_data = examples.get_contractor_dashboard_data(contractor_id, days_back)
        
        # Convert to JSON-serializable format
        jobs_data = []
        for job in dashboard_data['jobs']:
            jobs_data.append({
                'id': job.id,
                'version': job.version,
                'title': job.title,
                'status': job.status,
                'rate': str(job.rate),
            })
        
        timelogs_data = []
        for timelog in dashboard_data['timelogs']:
            timelogs_data.append({
                'id': timelog.id,
                'version': timelog.version,
                'duration_hours': round(timelog.duration / (1000 * 60 * 60), 2),
                'type': timelog.type,
            })
        
        payments_data = []
        for payment in dashboard_data['payment_items']:
            payments_data.append({
                'id': payment.id,
                'version': payment.version,
                'amount': str(payment.amount),
                'status': payment.status,
            })
        
        return JsonResponse({
            'contractor_id': contractor_id,
            'period_days': days_back,
            'summary': {
                'total_jobs': len(jobs_data),
                'total_hours': dashboard_data['total_hours'],
                'total_amount': str(dashboard_data['total_amount']),
            },
            'jobs': jobs_data,
            'timelogs': timelogs_data,
            'payments': payments_data,
            'note': 'Comprehensive contractor dashboard using SCD abstraction'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def company_report(request, company_id):
    """
    Company spending report using SCD abstraction
    """
    try:
        # Get month/year from query params
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
        
        # Use SCD abstraction
        examples = SCDQueryExamples()
        report_data = examples.get_company_spending_report(company_id, month, year)
        
        return JsonResponse({
            'company_id': company_id,
            'report': report_data,
            'note': 'Company spending report using SCD abstraction'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 