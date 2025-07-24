"""
SCD Manager - Abstraction layer for Slowly Changing Dimensions

This module provides a high-level abstraction for working with SCD models,
hiding the complexity of version management and latest-version queries.
"""

import logging
from typing import Type, Dict, Any, List, Optional, Union
from django.db import models, transaction
from django.db.models import Max, Q, Subquery, OuterRef
from django.core.exceptions import ObjectDoesNotExist

from .models import SCDModelMixin

logger = logging.getLogger(__name__)


class SCDQuerySet(models.QuerySet):
    """
    Custom QuerySet for SCD models that provides helper methods
    for common SCD operations.
    """
    
    def latest_versions(self):
        """
        Returns only the latest version of each record.
        
        This is the core optimization - uses a subquery to efficiently
        filter to only the latest version of each business ID.
        """
        # Create a subquery to get the maximum version for each business ID
        latest_versions_subquery = self.model.objects.values('id').annotate(
            max_version=Max('version')
        ).values('id', 'max_version')
        
        # Build filter conditions for the latest versions
        latest_filter = Q()
        for item in latest_versions_subquery:
            latest_filter |= Q(id=item['id'], version=item['max_version'])
        
        return self.filter(latest_filter)
    
    def latest_versions_optimized(self):
        """
        Optimized version using raw SQL for better performance on large datasets.
        This approach is more efficient for millions of records.
        """
        model_table = self.model._meta.db_table
        
        raw_sql = f"""
        SELECT t1.* FROM {model_table} t1
        INNER JOIN (
            SELECT id, MAX(version) as max_version 
            FROM {model_table} 
            GROUP BY id
        ) t2 ON t1.id = t2.id AND t1.version = t2.max_version
        """
        
        return self.extra(
            where=[f"{model_table}.uid IN (SELECT uid FROM ({raw_sql}) subq)"]
        )
    
    def for_business_ids(self, business_ids: List[str]):
        """Filter by business IDs (not UIDs)"""
        return self.filter(id__in=business_ids)
    
    def created_between(self, start_date, end_date):
        """Filter by creation date range"""
        return self.filter(created_at__range=[start_date, end_date])


class SCDManager(models.Manager):
    """
    Custom manager for SCD models.
    Provides the get_queryset method that returns our custom SCDQuerySet.
    """
    
    def get_queryset(self):
        return SCDQuerySet(self.model, using=self._db)
    
    def latest_versions(self):
        """Get all latest versions"""
        return self.get_queryset().latest_versions()


class SCDAbstraction:
    """
    High-level abstraction for SCD operations.
    
    This class provides a simple interface for developers to work with SCD models
    without having to understand the underlying version management complexity.
    """
    
    def __init__(self, model_class: Type[SCDModelMixin]):
        self.model_class = model_class
        self.model_name = model_class.__name__
    
    def get_latest_records(self, filters: Dict[str, Any] = None) -> models.QuerySet:
        """
        Get latest versions of records with optional filtering.
        
        Args:
            filters: Django ORM filter dict (e.g., {'status': 'active'})
        
        Returns:
            QuerySet of latest version records
        """
        # Get the latest version for each business ID
        latest_versions_subquery = self.model_class.objects.values('id').annotate(
            max_version=Max('version')
        ).values('id', 'max_version')
        
        # Build filter conditions for the latest versions
        latest_filter = Q()
        for item in latest_versions_subquery:
            latest_filter |= Q(id=item['id'], version=item['max_version'])
        
        # Start with the latest version filter
        queryset = self.model_class.objects.filter(latest_filter)
        
        # Apply additional filters if provided
        if filters:
            queryset = queryset.filter(**filters)
        
        logger.debug(f"Getting latest {self.model_name} records with filters: {filters}")
        return queryset
    
    def get_by_business_id(self, business_id: str, version: Optional[int] = None) -> models.Model:
        """
        Get a specific record by business ID.
        
        Args:
            business_id: The business ID
            version: Specific version (if None, returns latest)
        
        Returns:
            Model instance
        """
        if version is None:
            # Get latest version using the abstraction method
            latest_records = self.get_latest_records({'id': business_id})
            return latest_records.first()
        else:
            # Get specific version
            return self.model_class.objects.get(id=business_id, version=version)
    
    def create_record(self, business_id: str, **fields) -> models.Model:
        """
        Create a new SCD record (version 1).
        
        Args:
            business_id: The business ID for this record
            **fields: Field values for the record
        
        Returns:
            Created model instance
        """
        # Check if business_id already exists
        existing = self.model_class.objects.filter(id=business_id).exists()
        if existing:
            raise ValueError(f"Record with business_id '{business_id}' already exists. Use update_record() instead.")
        
        record = self.model_class(
            id=business_id,
            version=1,
            **fields
        )
        record.save()
        
        logger.info(f"Created new {self.model_name} record: {business_id} v1")
        return record
    
    def update_record(self, business_id: str, **updates) -> models.Model:
        """
        Update a record by creating a new version.
        
        Args:
            business_id: The business ID to update
            **updates: Fields to update
        
        Returns:
            New version of the record
        """
        # Get the latest version
        try:
            latest = self.get_by_business_id(business_id)
            if not latest:
                raise ObjectDoesNotExist(f"No record found with business_id: {business_id}")
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"No record found with business_id: {business_id}")
        
        # Create new version
        new_version = latest.version + 1
        
        # Copy all fields from latest version
        new_record_data = {}
        for field in self.model_class._meta.fields:
            if field.name not in ['uid', 'version', 'created_at', 'updated_at']:
                new_record_data[field.name] = getattr(latest, field.name)
        
        # Apply updates
        new_record_data.update(updates)
        new_record_data['version'] = new_version
        
        new_record = self.model_class(**new_record_data)
        new_record.save()
        
        logger.info(f"Updated {self.model_name} record: {business_id} v{latest.version} -> v{new_version}")
        return new_record
    
    def get_version_history(self, business_id: str) -> models.QuerySet:
        """
        Get all versions of a record ordered by version.
        
        Args:
            business_id: The business ID
        
        Returns:
            QuerySet of all versions
        """
        return self.model_class.objects.filter(id=business_id).order_by('version')
    
    def bulk_get_latest(self, business_ids: List[str]) -> models.QuerySet:
        """
        Efficiently get latest versions for multiple business IDs.
        
        Args:
            business_ids: List of business IDs
        
        Returns:
            QuerySet of latest versions
        """
        return self.model_class.objects.filter(
            id__in=business_ids
        ).latest_versions()


class SCDRelationshipHelper:
    """
    Helper class for managing relationships in SCD models.
    """
    
    @staticmethod
    def get_related_latest_records(source_queryset, related_field: str, 
                                 related_model: Type[SCDModelMixin]) -> Dict[str, models.Model]:
        """
        Get latest versions of related records for a queryset.
        
        This helps avoid N+1 queries when fetching related SCD records.
        
        Args:
            source_queryset: QuerySet of source records
            related_field: Field name that contains the related UID
            related_model: The related SCD model class
        
        Returns:
            Dict mapping UID to latest record
        """
        # Get all related UIDs
        related_uids = list(source_queryset.values_list(related_field, flat=True))
        
        # Get business IDs from UIDs
        business_ids = related_model.objects.filter(
            uid__in=related_uids
        ).values_list('id', flat=True)
        
        # Get latest versions
        latest_records = SCDAbstraction(related_model).bulk_get_latest(list(business_ids))
        
        # Create mapping from UID to record
        uid_to_record = {}
        for record in latest_records:
            uid_to_record[record.uid] = record
        
        return uid_to_record


# Convenience functions for common operations
def get_latest_jobs(**filters) -> models.QuerySet:
    """Get latest version of jobs with optional filters"""
    from .models import Job
    return SCDAbstraction(Job).get_latest_records(filters)


def get_latest_timelogs(**filters) -> models.QuerySet:
    """Get latest version of timelogs with optional filters"""
    from .models import Timelog
    return SCDAbstraction(Timelog).get_latest_records(filters)


def get_latest_payment_line_items(**filters) -> models.QuerySet:
    """Get latest version of payment line items with optional filters"""
    from .models import PaymentLineItem
    return SCDAbstraction(PaymentLineItem).get_latest_records(filters)


def update_job(business_id: str, **updates) -> models.Model:
    """Update a job by creating a new version"""
    from .models import Job
    return SCDAbstraction(Job).update_record(business_id, **updates)


def update_timelog(business_id: str, **updates) -> models.Model:
    """Update a timelog by creating a new version"""
    from .models import Timelog
    return SCDAbstraction(Timelog).update_record(business_id, **updates)


def update_payment_line_item(business_id: str, **updates) -> models.Model:
    """Update a payment line item by creating a new version"""
    from .models import PaymentLineItem
    return SCDAbstraction(PaymentLineItem).update_record(business_id, **updates) 