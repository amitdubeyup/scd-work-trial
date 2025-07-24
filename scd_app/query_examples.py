"""
SCD Query Examples - Demonstrating the abstraction

This module shows how the SCD abstraction simplifies the 4 required query patterns:
1. Get all active Jobs for a company (latest version filtering)
2. Get all active Jobs for a contractor (latest version filtering)
3. Get all PaymentLineItems for a contractor in a time period (latest versions only)
4. Get all Timelogs for a contractor in a time period (latest versions only)
"""

from datetime import datetime, timedelta
from django.db.models import Q, Max, F, Subquery, OuterRef
from .models import Job, Timelog, PaymentLineItem, Company, Contractor
from .scd_manager import SCDAbstraction, get_latest_jobs, get_latest_timelogs, get_latest_payment_line_items


class SCDQueryExamples:
    """
    Examples showing before/after the SCD abstraction.
    
    These examples demonstrate how the abstraction simplifies complex SCD queries
    and improves performance for large datasets.
    """
    
    def __init__(self):
        self.job_scd = SCDAbstraction(Job)
        self.timelog_scd = SCDAbstraction(Timelog)
        self.payment_scd = SCDAbstraction(PaymentLineItem)
    
    # ============================================================================
    # QUERY PATTERN 1: Get all active Jobs for a company
    # ============================================================================
    
    def get_active_jobs_for_company_old_way(self, company_id: str):
        """
        OLD WAY: Complex SCD query with manual latest version handling
        """
        # This is what developers had to write before the abstraction
        from django.db.models import Max
        
        # Subquery to get latest versions for each job id
        latest_versions_subquery = Job.objects.filter(
            id=OuterRef('id')
        ).aggregate(max_version=Max('version'))['max_version']
        
        jobs = Job.objects.annotate(
            max_version=Subquery(
                Job.objects.filter(
                    id=OuterRef('id')
                ).values('id').annotate(max_ver=Max('version')).values('max_ver')
            )
        ).filter(
            version=F('max_version'),
            company_id=company_id,
            status='active'
        )
        
        return jobs
    
    def get_active_jobs_for_company_new_way(self, company_id: str):
        """
        NEW WAY: Simple and clean using SCD abstraction
        """
        return self.job_scd.get_latest_records({
            'company_id': company_id,
            'status': 'active'
        })
    
    def get_active_jobs_for_company_convenience(self, company_id: str):
        """
        CONVENIENCE FUNCTION: Even simpler one-liner
        """
        return get_latest_jobs(company_id=company_id, status='active')
    
    # ============================================================================
    # QUERY PATTERN 2: Get all active Jobs for a contractor
    # ============================================================================
    
    def get_active_jobs_for_contractor_old_way(self, contractor_id: str):
        """
        OLD WAY: Manual SCD handling
        """
        # Complex query with manual version management
        latest_job_versions = Job.objects.values('id').annotate(
            max_version=Max('version')
        ).values('id', 'max_version')
        
        # Build complex filter
        version_filters = Q()
        for item in latest_job_versions:
            version_filters |= Q(id=item['id'], version=item['max_version'])
        
        return Job.objects.filter(
            version_filters,
            contractor_id=contractor_id,
            status='active'
        )
    
    def get_active_jobs_for_contractor_new_way(self, contractor_id: str):
        """
        NEW WAY: Clean and simple
        """
        return self.job_scd.get_latest_records({
            'contractor_id': contractor_id,
            'status': 'active'
        })
    
    # ============================================================================
    # QUERY PATTERN 3: Get PaymentLineItems for contractor in time period
    # ============================================================================
    
    def get_payment_line_items_for_contractor_old_way(self, contractor_id: str, 
                                                     start_date: datetime, 
                                                     end_date: datetime):
        """
        OLD WAY: Complex joins and subqueries
        """
        # First, get latest job versions for the contractor
        latest_jobs = Job.objects.values('id').annotate(
            max_version=Max('version')
        ).filter(contractor_id=contractor_id)
        
        job_uids = []
        for job_data in latest_jobs:
            latest_job = Job.objects.get(id=job_data['id'], version=job_data['max_version'])
            job_uids.append(latest_job.uid)
        
        # Then get latest payment line items
        latest_payments = PaymentLineItem.objects.values('id').annotate(
            max_version=Max('version')
        ).filter(
            job_uid__in=job_uids,
            created_at__range=[start_date, end_date]
        )
        
        # Finally, filter to actual latest versions
        payment_items = []
        for payment_data in latest_payments:
            latest_payment = PaymentLineItem.objects.get(
                id=payment_data['id'], 
                version=payment_data['max_version']
            )
            payment_items.append(latest_payment)
        
        return payment_items
    
    def get_payment_line_items_for_contractor_new_way(self, contractor_id: str, 
                                                     start_date: datetime, 
                                                     end_date: datetime):
        """
        NEW WAY: Much simpler with abstraction
        """
        # Get latest jobs for contractor
        job_uids = list(
            self.job_scd.get_latest_records({'contractor_id': contractor_id})
            .values_list('uid', flat=True)
        )
        
        # Get latest payment line items for those jobs in the time period
        return self.payment_scd.get_latest_records({
            'job_uid__in': job_uids
        }).filter(created_at__range=[start_date, end_date])
    
    def get_payment_line_items_for_contractor_optimized(self, contractor_id: str, 
                                                       start_date: datetime, 
                                                       end_date: datetime):
        """
        OPTIMIZED WAY: Using convenience function with date filtering
        """
        # Get job UIDs
        job_uids = get_latest_jobs(contractor_id=contractor_id).values_list('uid', flat=True)
        
        # Get payment line items
        return get_latest_payment_line_items(
            job_uid__in=list(job_uids)
        ).filter(created_at__range=[start_date, end_date])
    
    # ============================================================================
    # QUERY PATTERN 4: Get Timelogs for contractor in time period
    # ============================================================================
    
    def get_timelogs_for_contractor_old_way(self, contractor_id: str, 
                                           start_timestamp: int, 
                                           end_timestamp: int):
        """
        OLD WAY: Multiple queries and manual version handling
        """
        # Get all job versions for contractor
        contractor_jobs = Job.objects.filter(contractor_id=contractor_id)
        
        # Group by business ID and find latest versions
        latest_job_uids = []
        job_groups = {}
        for job in contractor_jobs:
            if job.id not in job_groups:
                job_groups[job.id] = []
            job_groups[job.id].append(job)
        
        for business_id, versions in job_groups.items():
            latest_version = max(versions, key=lambda x: x.version)
            latest_job_uids.append(latest_version.uid)
        
        # Get timelogs for those jobs
        timelogs = Timelog.objects.filter(
            job_uid__in=latest_job_uids,
            time_start__gte=start_timestamp,
            time_end__lte=end_timestamp
        )
        
        # Filter to latest versions of timelogs
        latest_timelogs = []
        timelog_groups = {}
        for timelog in timelogs:
            if timelog.id not in timelog_groups:
                timelog_groups[timelog.id] = []
            timelog_groups[timelog.id].append(timelog)
        
        for business_id, versions in timelog_groups.items():
            latest_version = max(versions, key=lambda x: x.version)
            latest_timelogs.append(latest_version)
        
        return latest_timelogs
    
    def get_timelogs_for_contractor_new_way(self, contractor_id: str, 
                                           start_timestamp: int, 
                                           end_timestamp: int):
        """
        NEW WAY: Clean and efficient
        """
        # Get latest job UIDs for contractor
        job_uids = list(
            self.job_scd.get_latest_records({'contractor_id': contractor_id})
            .values_list('uid', flat=True)
        )
        
        # Get latest timelogs for those jobs in the time period
        return self.timelog_scd.get_latest_records({
            'job_uid__in': job_uids,
            'time_start__gte': start_timestamp,
            'time_end__lte': end_timestamp
        })
    
    # ============================================================================
    # ADVANCED EXAMPLES: Performance optimizations for large datasets
    # ============================================================================
    
    def get_contractor_dashboard_data(self, contractor_id: str, days_back: int = 30):
        """
        Example: Getting all related data for a contractor dashboard
        Demonstrates efficient queries for millions of records
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        # Get all latest jobs for contractor
        jobs = self.job_scd.get_latest_records({'contractor_id': contractor_id})
        job_uids = list(jobs.values_list('uid', flat=True))
        
        # Get related data efficiently (avoiding N+1 queries)
        timelogs = self.timelog_scd.get_latest_records({
            'job_uid__in': job_uids,
            'time_start__gte': start_timestamp,
            'time_end__lte': end_timestamp
        })
        
        payment_items = self.payment_scd.get_latest_records({
            'job_uid__in': job_uids
        }).filter(created_at__range=[start_date, end_date])
        
        return {
            'jobs': jobs,
            'timelogs': timelogs,
            'payment_items': payment_items,
            'total_hours': sum(t.duration for t in timelogs) / (1000 * 60 * 60),  # Convert ms to hours
            'total_amount': sum(p.amount for p in payment_items),
        }
    
    def get_company_spending_report(self, company_id: str, month: int, year: int):
        """
        Example: Company spending report
        Shows how to efficiently aggregate SCD data
        """
        # Date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get latest jobs for company
        jobs = self.job_scd.get_latest_records({'company_id': company_id})
        job_uids = list(jobs.values_list('uid', flat=True))
        
        # Get payment line items for that period
        payments = self.payment_scd.get_latest_records({
            'job_uid__in': job_uids,
            'status': 'paid'
        }).filter(payment_date__range=[start_date, end_date])
        
        # Aggregate data
        total_paid = sum(p.amount for p in payments)
        job_breakdown = {}
        
        for payment in payments:
            job_id = next(j.id for j in jobs if j.uid == payment.job_uid)
            if job_id not in job_breakdown:
                job_breakdown[job_id] = 0
            job_breakdown[job_id] += payment.amount
        
        return {
            'period': f"{year}-{month:02d}",
            'total_paid': total_paid,
            'payment_count': len(payments),
            'job_breakdown': job_breakdown,
        }


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def demonstrate_query_improvements():
    """
    Function to demonstrate the before/after query improvements.
    Run this to see the actual SQL generated and performance differences.
    """
    examples = SCDQueryExamples()
    
    print("=== SCD Query Abstraction Demo ===\n")
    
    # Example company and contractor IDs
    company_id = "comp_demo123"
    contractor_id = "cont_demo456"
    
    print("1. Getting active jobs for company (old vs new):")
    print("   OLD WAY: Complex subqueries and annotations")
    old_jobs = examples.get_active_jobs_for_company_old_way(company_id)
    print(f"   Query: {old_jobs.query}")
    
    print("\n   NEW WAY: Simple and clean")
    new_jobs = examples.get_active_jobs_for_company_new_way(company_id)
    print(f"   Query: {new_jobs.query}")
    
    print("\n" + "="*50 + "\n")
    
    print("2. Getting payment line items for contractor:")
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    print("   NEW WAY (optimized):")
    payments = examples.get_payment_line_items_for_contractor_optimized(
        contractor_id, start_date, end_date
    )
    print(f"   Query: {payments.query}")
    
    return {
        'old_jobs': old_jobs,
        'new_jobs': new_jobs,
        'payments': payments
    }


def run_performance_test():
    """
    Performance test to compare old vs new approaches.
    This would be useful with actual data.
    """
    import time
    
    examples = SCDQueryExamples()
    company_id = "comp_test123"
    
    print("=== Performance Test ===")
    
    # Test new way
    start_time = time.time()
    new_result = examples.get_active_jobs_for_company_new_way(company_id)
    list(new_result)  # Force evaluation
    new_time = time.time() - start_time
    
    print(f"New abstraction method: {new_time:.4f} seconds")
    print(f"SQL Query: {new_result.query}")
    
    return new_time 