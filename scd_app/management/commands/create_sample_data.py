"""
Management command to create sample SCD data for testing and demonstration
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random

from scd_app.models import Company, Contractor, Job, Timelog, PaymentLineItem
from scd_app.scd_manager import SCDAbstraction


class Command(BaseCommand):
    help = 'Create sample SCD data for testing and demonstration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--companies',
            type=int,
            default=3,
            help='Number of companies to create'
        )
        parser.add_argument(
            '--contractors',
            type=int,
            default=5,
            help='Number of contractors to create'
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=10,
            help='Number of jobs to create'
        )
        parser.add_argument(
            '--versions',
            type=int,
            default=3,
            help='Average number of versions per SCD record'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample SCD data...'))
        
        # Clear existing data if requested
        if options['clear']:
            self.clear_existing_data()
        
        companies = self.create_companies(options['companies'])
        contractors = self.create_contractors(options['contractors'])
        jobs = self.create_jobs(companies, contractors, options['jobs'], options['versions'])
        timelogs = self.create_timelogs(jobs, options['versions'])
        payments = self.create_payment_line_items(jobs, timelogs, options['versions'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'  - {len(companies)} companies\n'
                f'  - {len(contractors)} contractors\n'
                f'  - {Job.objects.count()} job records ({len(jobs)} unique jobs)\n'
                f'  - {Timelog.objects.count()} timelog records ({len(timelogs)} unique timelogs)\n'
                f'  - {PaymentLineItem.objects.count()} payment records ({len(payments)} unique payments)'
            )
        )
    
    def clear_existing_data(self):
        """Clear all existing sample data"""
        self.stdout.write('Clearing existing data...')
        
        # Delete in order to respect foreign key constraints
        PaymentLineItem.objects.all().delete()
        Timelog.objects.all().delete()
        Job.objects.all().delete()
        Contractor.objects.all().delete()
        Company.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))
    
    def create_companies(self, count):
        """Create sample companies"""
        companies = []
        created_count = 0
        for i in range(count):
            company, created = Company.objects.get_or_create(
                id=f"comp_{i+1:03d}",
                defaults={
                    'name': f"Company {i+1}",
                    'email': f"company{i+1}@example.com"
                }
            )
            companies.append(company)
            if created:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} companies ({count - created_count} already existed)')
        return companies
    
    def create_contractors(self, count):
        """Create sample contractors"""
        contractors = []
        created_count = 0
        for i in range(count):
            contractor, created = Contractor.objects.get_or_create(
                id=f"cont_{i+1:03d}",
                defaults={
                    'name': f"Contractor {i+1}",
                    'email': f"contractor{i+1}@example.com"
                }
            )
            contractors.append(contractor)
            if created:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} contractors ({count - created_count} already existed)')
        return contractors
    
    def create_jobs(self, companies, contractors, count, avg_versions):
        """Create sample jobs with multiple versions"""
        job_scd = SCDAbstraction(Job)
        jobs = []
        
        job_titles = [
            'Software Engineer', 'Senior Developer', 'DevOps Engineer',
            'Data Scientist', 'Product Manager', 'UI/UX Designer',
            'Machine Learning Engineer', 'Full Stack Developer',
            'Backend Developer', 'Frontend Developer'
        ]
        
        statuses = ['active', 'extended', 'paused', 'completed']
        
        for i in range(count):
            company = random.choice(companies)
            contractor = random.choice(contractors)
            
            business_id = f"job_{i+1:03d}"
            
            # Check if job already exists
            existing_job = job_scd.get_latest_records({'id': business_id}).first()
            if existing_job:
                self.stdout.write(f'Job {business_id} already exists, skipping...')
                jobs.append(business_id)
                continue
            
            # Create initial version
            job = job_scd.create_record(
                business_id=business_id,
                title=random.choice(job_titles),
                status='active',
                rate=round(random.uniform(20.0, 50.0), 2),
                description=f"Description for job {i+1}",
                company_id=company.id,
                contractor_id=contractor.id
            )
            
            # Create additional versions
            versions_to_create = random.randint(1, avg_versions)
            for v in range(versions_to_create - 1):
                updates = {}
                
                # Randomly update fields
                if random.random() < 0.3:  # 30% chance to update status
                    updates['status'] = random.choice(statuses)
                
                if random.random() < 0.4:  # 40% chance to update rate
                    updates['rate'] = round(random.uniform(20.0, 60.0), 2)
                
                if random.random() < 0.2:  # 20% chance to update title
                    updates['title'] = random.choice(job_titles)
                
                if updates:
                    job = job_scd.update_record(business_id, **updates)
            
            jobs.append(business_id)
        
        self.stdout.write(f'Created {count} jobs with versions')
        return jobs
    
    def create_timelogs(self, jobs, avg_versions):
        """Create sample timelogs"""
        timelog_scd = SCDAbstraction(Timelog)
        timelogs = []
        
        # Get latest job versions to get UIDs
        job_scd = SCDAbstraction(Job)
        latest_jobs = job_scd.get_latest_records()
        job_uids = [job.uid for job in latest_jobs]
        
        types = ['captured', 'adjusted', 'manual']
        
        # Create 2-5 timelogs per job
        for i, job_business_id in enumerate(jobs):
            num_timelogs = random.randint(2, 5)
            
            for t in range(num_timelogs):
                business_id = f"timelog_{i+1:03d}_{t+1:02d}"
                
                # Check if timelog already exists
                existing_timelog = timelog_scd.get_latest_records({'id': business_id}).first()
                if existing_timelog:
                    timelogs.append(business_id)
                    continue
                
                # Random time range in the last 30 days
                days_ago = random.randint(0, 30)
                start_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(8, 16))
                duration_hours = random.uniform(0.5, 8.0)
                duration_ms = int(duration_hours * 60 * 60 * 1000)
                end_time = start_time + timedelta(milliseconds=duration_ms)
                
                job_uid = random.choice(job_uids)
                
                # Create initial version
                timelog = timelog_scd.create_record(
                    business_id=business_id,
                    duration=duration_ms,
                    time_start=int(start_time.timestamp() * 1000),
                    time_end=int(end_time.timestamp() * 1000),
                    type='captured',
                    job_uid=job_uid
                )
                
                # Maybe create adjusted version
                if random.random() < 0.3:  # 30% chance of adjustment
                    adjusted_duration = int(duration_ms * random.uniform(0.7, 1.3))
                    timelog = timelog_scd.update_record(
                        business_id,
                        duration=adjusted_duration,
                        type='adjusted'
                    )
                
                timelogs.append(business_id)
        
        self.stdout.write(f'Created timelogs for jobs')
        return timelogs
    
    def create_payment_line_items(self, jobs, timelogs, avg_versions):
        """Create sample payment line items"""
        payment_scd = SCDAbstraction(PaymentLineItem)
        payments = []
        
        # Get latest versions
        job_scd = SCDAbstraction(Job)
        timelog_scd = SCDAbstraction(Timelog)
        
        latest_jobs = job_scd.get_latest_records()
        latest_timelogs = timelog_scd.get_latest_records()
        
        job_uids = [job.uid for job in latest_jobs]
        timelog_uids = [timelog.uid for timelog in latest_timelogs]
        
        statuses = ['not-paid', 'paid', 'pending', 'failed']
        
        # Create 1-2 payments per timelog
        for i, timelog_business_id in enumerate(timelogs):
            business_id = f"payment_{i+1:04d}"
            
            # Check if payment already exists
            existing_payment = payment_scd.get_latest_records({'id': business_id}).first()
            if existing_payment:
                payments.append(business_id)
                continue
            
            amount = round(random.uniform(50.0, 500.0), 2)
            
            # Create initial version
            payment = payment_scd.create_record(
                business_id=business_id,
                amount=amount,
                status='not-paid',
                job_uid=random.choice(job_uids),
                timelog_uid=random.choice(timelog_uids),
                notes=f"Payment for timelog {timelog_business_id}"
            )
            
            # Maybe update status
            if random.random() < 0.7:  # 70% chance of status change
                new_status = random.choice(statuses)
                payment_date = None
                if new_status == 'paid':
                    payment_date = timezone.now() - timedelta(days=random.randint(0, 10))
                
                payment = payment_scd.update_record(
                    business_id,
                    status=new_status,
                    payment_date=payment_date
                )
            
            payments.append(business_id)
        
        self.stdout.write(f'Created payment line items')
        return payments 