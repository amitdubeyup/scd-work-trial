"""
SCD Models - Slowly Changing Dimensions implementation

This module contains the core SCD models for Jobs, Timelogs, and PaymentLineItems.
Each model follows the SCD pattern with (id, version) as unique key and uid as primary key.
"""

import uuid
from django.db import models
from django.utils import timezone


class SCDModelMixin(models.Model):
    """
    Base mixin for SCD (Slowly Changing Dimensions) models.
    
    Provides common SCD fields:
    - id: Business identifier (stays same across versions)
    - version: Version number (increments with each change)
    - uid: Unique identifier for this specific version (primary key)
    - created_at: When this version was created
    - updated_at: When this version was last updated
    """
    
    # SCD Core Fields
    id = models.CharField(max_length=255, db_index=True, help_text="Business ID (same across versions)")
    version = models.PositiveIntegerField(help_text="Version number")
    uid = models.CharField(max_length=255, primary_key=True, help_text="Unique ID for this version")
    
    # Audit Fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        unique_together = ['id', 'version']
        indexes = [
            models.Index(fields=['id', 'version']),
            models.Index(fields=['id']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Generate UID if not provided"""
        if not self.uid:
            # Generate UID with model-specific prefix
            model_prefix = self.__class__.__name__.lower()
            self.uid = f"{model_prefix}_uid_{uuid.uuid4().hex[:20]}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, version={self.version})"


class Job(SCDModelMixin):
    """
    Job model with SCD implementation.
    
    Represents job postings that can change over time (status, rate, etc.)
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('extended', 'Extended'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Business Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Hourly rate")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Foreign Keys
    company_id = models.CharField(max_length=255, db_index=True)
    contractor_id = models.CharField(max_length=255, db_index=True)
    
    class Meta:
        db_table = 'scd_jobs'
        indexes = [
            models.Index(fields=['company_id']),
            models.Index(fields=['contractor_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Job({self.id}): {self.title} - {self.status} (v{self.version})"


class Timelog(SCDModelMixin):
    """
    Timelog model with SCD implementation.
    
    Represents time tracking entries that can be adjusted over time.
    """
    
    TYPE_CHOICES = [
        ('captured', 'Captured'),
        ('adjusted', 'Adjusted'),
        ('manual', 'Manual'),
    ]
    
    # Business Fields
    duration = models.PositiveIntegerField(help_text="Duration in milliseconds")
    time_start = models.BigIntegerField(help_text="Start timestamp (milliseconds)")
    time_end = models.BigIntegerField(help_text="End timestamp (milliseconds)")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='captured')
    description = models.TextField(blank=True)
    
    # Foreign Key to specific Job version
    job_uid = models.CharField(max_length=255, db_index=True, help_text="References specific Job version")
    
    class Meta:
        db_table = 'scd_timelogs'
        indexes = [
            models.Index(fields=['job_uid']),
            models.Index(fields=['type']),
            models.Index(fields=['time_start']),
            models.Index(fields=['time_end']),
        ]
    
    def __str__(self):
        return f"Timelog({self.id}): {self.duration}ms - {self.type} (v{self.version})"


class PaymentLineItem(SCDModelMixin):
    """
    PaymentLineItem model with SCD implementation.
    
    Represents payment ledger entries that can change status over time.
    """
    
    STATUS_CHOICES = [
        ('not-paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Business Fields
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not-paid')
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Foreign Keys to specific versions
    job_uid = models.CharField(max_length=255, db_index=True, help_text="References specific Job version")
    timelog_uid = models.CharField(max_length=255, db_index=True, help_text="References specific Timelog version")
    
    class Meta:
        db_table = 'scd_payment_line_items'
        indexes = [
            models.Index(fields=['job_uid']),
            models.Index(fields=['timelog_uid']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f"PaymentLineItem({self.id}): ${self.amount} - {self.status} (v{self.version})"


# Helper models for relationships (non-SCD)
class Company(models.Model):
    """Company model (not SCD - companies don't change frequently)"""
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'companies'
    
    def __str__(self):
        return self.name


class Contractor(models.Model):
    """Contractor model (not SCD - contractors don't change frequently)"""
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'contractors'
    
    def __str__(self):
        return self.name 