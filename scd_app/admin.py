"""
Django admin configuration for SCD models
"""

from django.contrib import admin
from .models import Job, Timelog, PaymentLineItem, Company, Contractor


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at']


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'version', 'uid', 'title', 'status', 'rate', 'company_id', 'contractor_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'uid', 'title', 'company_id', 'contractor_id']
    readonly_fields = ['uid', 'created_at', 'updated_at']
    ordering = ['-created_at', 'id', '-version']
    
    fieldsets = (
        ('SCD Fields', {
            'fields': ('id', 'version', 'uid')
        }),
        ('Job Details', {
            'fields': ('title', 'description', 'status', 'rate')
        }),
        ('Relationships', {
            'fields': ('company_id', 'contractor_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Timelog)
class TimelogAdmin(admin.ModelAdmin):
    list_display = ['id', 'version', 'uid', 'duration_hours', 'type', 'job_uid', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['id', 'uid', 'job_uid']
    readonly_fields = ['uid', 'created_at', 'updated_at', 'duration_hours']
    ordering = ['-created_at', 'id', '-version']
    
    def duration_hours(self, obj):
        """Convert duration from milliseconds to hours"""
        return round(obj.duration / (1000 * 60 * 60), 2)
    duration_hours.short_description = 'Duration (hours)'
    
    fieldsets = (
        ('SCD Fields', {
            'fields': ('id', 'version', 'uid')
        }),
        ('Time Details', {
            'fields': ('duration', 'duration_hours', 'time_start', 'time_end', 'type')
        }),
        ('Relationships', {
            'fields': ('job_uid',)
        }),
        ('Additional', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentLineItem)
class PaymentLineItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'version', 'uid', 'amount', 'status', 'job_uid', 'payment_date', 'created_at']
    list_filter = ['status', 'payment_date', 'created_at']
    search_fields = ['id', 'uid', 'job_uid', 'timelog_uid']
    readonly_fields = ['uid', 'created_at', 'updated_at']
    ordering = ['-created_at', 'id', '-version']
    
    fieldsets = (
        ('SCD Fields', {
            'fields': ('id', 'version', 'uid')
        }),
        ('Payment Details', {
            'fields': ('amount', 'status', 'payment_date')
        }),
        ('Relationships', {
            'fields': ('job_uid', 'timelog_uid')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 