"""
Tests for SCD abstraction layer
"""

from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime, timedelta
import json

from .models import Job, Timelog, PaymentLineItem, Company, Contractor
from .scd_manager import SCDAbstraction, get_latest_jobs, get_latest_timelogs, get_latest_payment_line_items
from .query_examples import SCDQueryExamples


class SCDModelTest(TestCase):
    """Test SCD model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            id="comp_test123",
            name="Test Company",
            email="test@company.com"
        )
        
        self.contractor = Contractor.objects.create(
            id="cont_test456",
            name="Test Contractor", 
            email="test@contractor.com"
        )
    
    def test_job_scd_creation(self):
        """Test creating new SCD job record"""
        job_scd = SCDAbstraction(Job)
        
        # Create new job
        job = job_scd.create_record(
            business_id="job_test789",
            title="Software Engineer",
            status="active",
            rate=25.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
        
        self.assertEqual(job.id, "job_test789")
        self.assertEqual(job.version, 1)
        self.assertEqual(job.title, "Software Engineer")
        self.assertEqual(job.status, "active")
        self.assertTrue(job.uid.startswith("job_uid_"))
    
    def test_job_scd_update(self):
        """Test updating SCD job record (creates new version)"""
        job_scd = SCDAbstraction(Job)
        
        # Create initial job
        job_v1 = job_scd.create_record(
            business_id="job_update_test",
            title="Junior Developer",
            status="active",
            rate=20.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
        
        # Update job (creates version 2)
        job_v2 = job_scd.update_record(
            business_id="job_update_test",
            title="Senior Developer",
            rate=30.00
        )
        
        self.assertEqual(job_v2.id, "job_update_test")
        self.assertEqual(job_v2.version, 2)
        self.assertEqual(job_v2.title, "Senior Developer")
        self.assertEqual(job_v2.rate, 30.00)
        self.assertEqual(job_v2.status, "active")  # Unchanged field preserved
        
        # Verify both versions exist
        self.assertTrue(Job.objects.filter(id="job_update_test", version=1).exists())
        self.assertTrue(Job.objects.filter(id="job_update_test", version=2).exists())
    
    def test_latest_version_query(self):
        """Test getting latest versions of records"""
        job_scd = SCDAbstraction(Job)
        
        # Create job with multiple versions
        job_v1 = job_scd.create_record(
            business_id="job_latest_test",
            title="Developer",
            status="active",
            rate=25.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
        
        job_v2 = job_scd.update_record("job_latest_test", rate=30.00)
        job_v3 = job_scd.update_record("job_latest_test", status="extended")
        
        # Get latest version
        latest_jobs = job_scd.get_latest_records()
        
        self.assertEqual(len(latest_jobs), 1)
        latest_job = latest_jobs.first()
        self.assertEqual(latest_job.version, 3)
        self.assertEqual(latest_job.status, "extended")
        self.assertEqual(latest_job.rate, 30.00)
    
    def test_multiple_jobs_latest_versions(self):
        """Test getting latest versions of multiple jobs"""
        job_scd = SCDAbstraction(Job)
        
        # Create multiple jobs with different versions
        job1_v1 = job_scd.create_record(
            business_id="job_multi_1",
            title="Job 1",
            status="active",
            rate=20.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
        job1_v2 = job_scd.update_record("job_multi_1", rate=25.00)
        
        job2_v1 = job_scd.create_record(
            business_id="job_multi_2",
            title="Job 2",
            status="active",
            rate=30.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
        
        # Get latest versions
        latest_jobs = job_scd.get_latest_records()
        
        self.assertEqual(len(latest_jobs), 2)
        
        # Check that we get the correct latest versions
        job1_latest = latest_jobs.filter(id="job_multi_1").first()
        job2_latest = latest_jobs.filter(id="job_multi_2").first()
        
        self.assertEqual(job1_latest.version, 2)
        self.assertEqual(job1_latest.rate, 25.00)
        
        self.assertEqual(job2_latest.version, 1)
        self.assertEqual(job2_latest.rate, 30.00)


class SCDAbstractionTest(TestCase):
    """Test the SCD abstraction layer"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            id="comp_abstraction_test",
            name="Abstraction Test Company",
            email="test@abstraction.com"
        )
        
        self.contractor = Contractor.objects.create(
            id="cont_abstraction_test",
            name="Abstraction Test Contractor",
            email="test@abstraction.com"
        )
        
        # Create test jobs
        job_scd = SCDAbstraction(Job)
        self.job1 = job_scd.create_record(
            business_id="job_abs_1",
            title="Test Job 1",
            status="active",
            rate=25.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
        
        self.job2 = job_scd.create_record(
            business_id="job_abs_2",
            title="Test Job 2",
            status="extended",
            rate=30.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
    
    def test_convenience_functions(self):
        """Test convenience functions for getting latest records"""
        # Test get_latest_jobs
        active_jobs = get_latest_jobs(status='active')
        self.assertEqual(len(active_jobs), 1)
        self.assertEqual(active_jobs.first().id, "job_abs_1")
        
        extended_jobs = get_latest_jobs(status='extended')
        self.assertEqual(len(extended_jobs), 1)
        self.assertEqual(extended_jobs.first().id, "job_abs_2")
        
        company_jobs = get_latest_jobs(company_id=self.company.id)
        self.assertEqual(len(company_jobs), 2)
        
        contractor_jobs = get_latest_jobs(contractor_id=self.contractor.id)
        self.assertEqual(len(contractor_jobs), 2)
    
    def test_timelog_scd_operations(self):
        """Test SCD operations on Timelog model"""
        timelog_scd = SCDAbstraction(Timelog)
        
        # Create timelog
        start_time = int(datetime.now().timestamp() * 1000)
        end_time = start_time + 3600000  # 1 hour later
        
        timelog_v1 = timelog_scd.create_record(
            business_id="timelog_test_1",
            duration=3600000,
            time_start=start_time,
            time_end=end_time,
            type="captured",
            job_uid=self.job1.uid
        )
        
        self.assertEqual(timelog_v1.type, "captured")
        self.assertEqual(timelog_v1.duration, 3600000)
        
        # Update timelog (adjust duration)
        timelog_v2 = timelog_scd.update_record(
            business_id="timelog_test_1",
            duration=3000000,  # Adjusted duration
            type="adjusted"
        )
        
        self.assertEqual(timelog_v2.version, 2)
        self.assertEqual(timelog_v2.type, "adjusted")
        self.assertEqual(timelog_v2.duration, 3000000)
        
        # Verify latest version
        latest_timelogs = get_latest_timelogs()
        self.assertEqual(len(latest_timelogs), 1)
        self.assertEqual(latest_timelogs.first().version, 2)
    
    def test_payment_line_item_scd(self):
        """Test SCD operations on PaymentLineItem model"""
        payment_scd = SCDAbstraction(PaymentLineItem)
        
        # Create payment line item
        payment_v1 = payment_scd.create_record(
            business_id="payment_test_1",
            amount=100.00,
            status="not-paid",
            job_uid=self.job1.uid,
            timelog_uid="timelog_uid_test"
        )
        
        self.assertEqual(payment_v1.status, "not-paid")
        self.assertEqual(payment_v1.amount, 100.00)
        
        # Update payment status
        payment_v2 = payment_scd.update_record(
            business_id="payment_test_1",
            status="paid",
            payment_date=datetime.now()
        )
        
        self.assertEqual(payment_v2.version, 2)
        self.assertEqual(payment_v2.status, "paid")
        self.assertIsNotNone(payment_v2.payment_date)
        
        # Verify latest version
        latest_payments = get_latest_payment_line_items()
        self.assertEqual(len(latest_payments), 1)
        self.assertEqual(latest_payments.first().status, "paid")


class SCDQueryExamplesTest(TestCase):
    """Test the query examples and patterns"""
    
    def setUp(self):
        """Set up comprehensive test data"""
        # Create companies and contractors
        self.company1 = Company.objects.create(
            id="comp_query_1", name="Query Company 1", email="query1@test.com"
        )
        self.company2 = Company.objects.create(
            id="comp_query_2", name="Query Company 2", email="query2@test.com"
        )
        
        self.contractor1 = Contractor.objects.create(
            id="cont_query_1", name="Query Contractor 1", email="cont1@test.com"
        )
        self.contractor2 = Contractor.objects.create(
            id="cont_query_2", name="Query Contractor 2", email="cont2@test.com"
        )
        
        # Create jobs with multiple versions
        job_scd = SCDAbstraction(Job)
        
        # Company 1 jobs
        self.job1 = job_scd.create_record(
            business_id="job_query_1",
            title="Job 1",
            status="active",
            rate=25.00,
            company_id=self.company1.id,
            contractor_id=self.contractor1.id
        )
        
        self.job2 = job_scd.create_record(
            business_id="job_query_2",
            title="Job 2",
            status="extended",
            rate=30.00,
            company_id=self.company1.id,
            contractor_id=self.contractor2.id
        )
        
        # Company 2 jobs
        self.job3 = job_scd.create_record(
            business_id="job_query_3",
            title="Job 3",
            status="active",
            rate=35.00,
            company_id=self.company2.id,
            contractor_id=self.contractor1.id
        )
        
        self.examples = SCDQueryExamples()
    
    def test_query_pattern_1_jobs_by_company(self):
        """Test Query Pattern 1: Get all active Jobs for a company"""
        # Test with company 1
        active_jobs_c1 = self.examples.get_active_jobs_for_company_new_way(self.company1.id)
        self.assertEqual(len(active_jobs_c1), 1)
        self.assertEqual(active_jobs_c1.first().id, "job_query_1")
        
        # Test with company 2
        active_jobs_c2 = self.examples.get_active_jobs_for_company_new_way(self.company2.id)
        self.assertEqual(len(active_jobs_c2), 1)
        self.assertEqual(active_jobs_c2.first().id, "job_query_3")
        
        # Test convenience function
        convenience_jobs = self.examples.get_active_jobs_for_company_convenience(self.company1.id)
        self.assertEqual(len(convenience_jobs), 1)
    
    def test_query_pattern_2_jobs_by_contractor(self):
        """Test Query Pattern 2: Get all active Jobs for a contractor"""
        # Contractor 1 has jobs from both companies
        contractor1_jobs = self.examples.get_active_jobs_for_contractor_new_way(self.contractor1.id)
        self.assertEqual(len(contractor1_jobs), 2)  # job1 and job3
        
        # Contractor 2 has one extended job (not active)
        contractor2_jobs = self.examples.get_active_jobs_for_contractor_new_way(self.contractor2.id)
        self.assertEqual(len(contractor2_jobs), 0)  # No active jobs
    
    def test_dashboard_data_retrieval(self):
        """Test contractor dashboard data retrieval"""
        dashboard_data = self.examples.get_contractor_dashboard_data(self.contractor1.id, days_back=30)
        
        self.assertIn('jobs', dashboard_data)
        self.assertIn('timelogs', dashboard_data)
        self.assertIn('payment_items', dashboard_data)
        self.assertIn('total_hours', dashboard_data)
        self.assertIn('total_amount', dashboard_data)
        
        # Should have 2 jobs for contractor 1
        self.assertEqual(len(dashboard_data['jobs']), 2)


class SCDAPITest(TestCase):
    """Test the API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = Client()
        
        # Create test data
        self.company = Company.objects.create(
            id="comp_api_test", name="API Test Company", email="api@test.com"
        )
        self.contractor = Contractor.objects.create(
            id="cont_api_test", name="API Test Contractor", email="api@test.com"
        )
        
        job_scd = SCDAbstraction(Job)
        self.job = job_scd.create_record(
            business_id="job_api_test",
            title="API Test Job",
            status="active",
            rate=25.00,
            company_id=self.company.id,
            contractor_id=self.contractor.id
        )
    
    def test_index_endpoint(self):
        """Test the index endpoint"""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('endpoints', data)
    
    def test_demo_endpoint(self):
        """Test the demo endpoint"""
        response = self.client.get('/api/demo/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('benefits', data)
    
    def test_jobs_by_company_endpoint(self):
        """Test Query Pattern 1 endpoint"""
        response = self.client.get(f'/api/jobs/company/{self.company.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['company_id'], self.company.id)
        self.assertEqual(len(data['jobs']), 1)
        self.assertEqual(data['jobs'][0]['id'], 'job_api_test')
    
    def test_jobs_by_contractor_endpoint(self):
        """Test Query Pattern 2 endpoint"""
        response = self.client.get(f'/api/jobs/contractor/{self.contractor.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['contractor_id'], self.contractor.id)
        self.assertEqual(len(data['jobs']), 1)
    
    def test_contractor_dashboard_endpoint(self):
        """Test contractor dashboard endpoint"""
        response = self.client.get(f'/api/dashboard/contractor/{self.contractor.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['contractor_id'], self.contractor.id)
        self.assertIn('summary', data)
        self.assertIn('jobs', data)


class SCDPerformanceTest(TestCase):
    """Test performance aspects of SCD abstraction"""
    
    def test_bulk_latest_version_query(self):
        """Test bulk operations for latest versions"""
        job_scd = SCDAbstraction(Job)
        
        # Create multiple jobs with versions
        company_id = "comp_perf_test"
        contractor_id = "cont_perf_test"
        
        Company.objects.create(id=company_id, name="Perf Test", email="perf@test.com")
        Contractor.objects.create(id=contractor_id, name="Perf Test", email="perf@test.com")
        
        # Create 10 jobs with 3 versions each
        for i in range(10):
            business_id = f"job_perf_{i}"
            
            # Version 1
            job_v1 = job_scd.create_record(
                business_id=business_id,
                title=f"Job {i}",
                status="active",
                rate=20.00,
                company_id=company_id,
                contractor_id=contractor_id
            )
            
            # Version 2
            job_v2 = job_scd.update_record(business_id, rate=25.00)
            
            # Version 3
            job_v3 = job_scd.update_record(business_id, status="extended")
        
        # Should have 30 total job records (10 * 3 versions)
        total_jobs = Job.objects.count()
        self.assertEqual(total_jobs, 30)
        
        # Should get 10 latest versions
        latest_jobs = job_scd.get_latest_records()
        self.assertEqual(len(latest_jobs), 10)
        
        # All should be version 3
        for job in latest_jobs:
            self.assertEqual(job.version, 3)
            self.assertEqual(job.status, "extended")
            self.assertEqual(job.rate, 25.00)
    
    def test_query_with_filters_performance(self):
        """Test performance of filtered queries"""
        job_scd = SCDAbstraction(Job)
        
        company_id = "comp_filter_test"
        Company.objects.create(id=company_id, name="Filter Test", email="filter@test.com")
        
        # Create jobs with different statuses
        for i in range(5):
            contractor_id = f"cont_filter_{i}"
            Contractor.objects.create(
                id=contractor_id, name=f"Contractor {i}", email=f"cont{i}@test.com"
            )
            
            job_scd.create_record(
                business_id=f"job_filter_{i}",
                title=f"Job {i}",
                status="active" if i % 2 == 0 else "extended",
                rate=25.00,
                company_id=company_id,
                contractor_id=contractor_id
            )
        
        # Test filtered queries
        active_jobs = job_scd.get_latest_records({'status': 'active'})
        extended_jobs = job_scd.get_latest_records({'status': 'extended'})
        company_jobs = job_scd.get_latest_records({'company_id': company_id})
        
        self.assertEqual(len(active_jobs), 3)  # Jobs 0, 2, 4
        self.assertEqual(len(extended_jobs), 2)  # Jobs 1, 3
        self.assertEqual(len(company_jobs), 5)  # All jobs 