# SCD Work Trial - API Documentation

Complete API request details for testing the Slowly Changing Dimensions (SCD) Django application.

## Base Configuration

- **Base URL**: `http://localhost:8000/api/`
- **HTTP Method**: All endpoints use `GET`
- **Response Format**: JSON
- **Content-Type**: `application/json`

## API Endpoints

### 1. Root/Index Endpoint

```
GET /api/
```

**Description**: Basic info about the SCD implementation and available endpoints

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "message": "SCD Work Trial - Django Implementation",
  "description": "Abstraction layer for Slowly Changing Dimensions",
  "endpoints": [
    "/api/demo/ - Query demonstrations",
    "/api/jobs/ - All latest jobs",
    "/api/jobs/company/<id>/ - Jobs by company",
    "/api/jobs/contractor/<id>/ - Jobs by contractor",
    "/api/timelogs/contractor/<id>/ - Timelogs by contractor",
    "/api/payments/contractor/<id>/ - Payments by contractor",
    "/api/dashboard/contractor/<id>/ - Contractor dashboard",
    "/api/report/company/<id>/ - Company spending report"
  ]
}
```

---

### 2. Demo Queries

```
GET /api/demo/
```

**Description**: Demonstrates SCD abstraction with example queries showing old vs new approaches

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/demo/" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "message": "SCD Query Demonstration",
  "note": "This shows how the abstraction simplifies complex SCD queries",
  "examples": {
    "old_jobs_sql": "SELECT ...",
    "new_jobs_sql": "SELECT ...",
    "payments_sql": "SELECT ..."
  },
  "benefits": [
    "Simplified query syntax",
    "Automatic latest version filtering",
    "Performance optimization for large datasets",
    "Reduced code duplication",
    "Developer-friendly interface"
  ]
}
```

---

### 3. All Jobs (Latest Versions)

```
GET /api/jobs/
```

**Description**: Get all latest version jobs using SCD abstraction

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/jobs/" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "jobs": [
    {
      "id": "job_001",
      "version": 2,
      "uid": "job_uid_abc123def456",
      "title": "Software Engineer",
      "status": "active",
      "rate": "45.50",
      "company_id": "comp_001",
      "contractor_id": "cont_001",
      "created_at": "2023-12-01T10:30:00Z"
    }
  ],
  "count": 10,
  "note": "All latest versions using SCD abstraction"
}
```

---

### 4. Jobs by Company

```
GET /api/jobs/company/<company_id>/
GET /api/jobs/company/<company_id>/?status=<status>
```

**Description**: Get all active jobs for a specific company (latest version filtering)

**Parameters**:
- `company_id` (path): Company identifier
- `status` (query, optional): Filter by status (default: 'active')
  - Valid values: `active`, `extended`, `paused`, `completed`, `cancelled`

**Example Requests**:
```bash
# All active jobs for company
curl -X GET "http://localhost:8000/api/jobs/company/comp_001/" \
  -H "Accept: application/json"

# All completed jobs for company
curl -X GET "http://localhost:8000/api/jobs/company/comp_001/?status=completed" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "company_id": "comp_001",
  "status_filter": "active",
  "jobs": [
    {
      "id": "job_001",
      "version": 2,
      "uid": "job_uid_abc123def456",
      "title": "Software Engineer",
      "status": "active",
      "rate": "45.50",
      "company_id": "comp_001",
      "contractor_id": "cont_001",
      "created_at": "2023-12-01T10:30:00Z"
    }
  ],
  "count": 3,
  "note": "Query Pattern 1: Latest jobs for company using SCD abstraction"
}
```

---

### 5. Jobs by Contractor

```
GET /api/jobs/contractor/<contractor_id>/
GET /api/jobs/contractor/<contractor_id>/?status=<status>
```

**Description**: Get all active jobs for a specific contractor (latest version filtering)

**Parameters**:
- `contractor_id` (path): Contractor identifier
- `status` (query, optional): Filter by status (default: 'active')

**Example Requests**:
```bash
# All active jobs for contractor
curl -X GET "http://localhost:8000/api/jobs/contractor/cont_001/" \
  -H "Accept: application/json"

# All paused jobs for contractor
curl -X GET "http://localhost:8000/api/jobs/contractor/cont_001/?status=paused" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "contractor_id": "cont_001",
  "status_filter": "active",
  "jobs": [
    {
      "id": "job_001",
      "version": 2,
      "uid": "job_uid_abc123def456",
      "title": "Software Engineer",
      "status": "active",
      "rate": "45.50",
      "company_id": "comp_001",
      "contractor_id": "cont_001",
      "created_at": "2023-12-01T10:30:00Z"
    }
  ],
  "count": 2,
  "note": "Query Pattern 2: Latest jobs for contractor using SCD abstraction"
}
```

---

### 6. Timelogs by Contractor

```
GET /api/timelogs/contractor/<contractor_id>/
GET /api/timelogs/contractor/<contractor_id>/?days=<number>
```

**Description**: Get all timelogs for a contractor in a time period (latest versions only)

**Parameters**:
- `contractor_id` (path): Contractor identifier
- `days` (query, optional): Number of days back to search (default: 30)

**Example Requests**:
```bash
# Last 30 days of timelogs
curl -X GET "http://localhost:8000/api/timelogs/contractor/cont_001/" \
  -H "Accept: application/json"

# Last 7 days of timelogs
curl -X GET "http://localhost:8000/api/timelogs/contractor/cont_001/?days=7" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "contractor_id": "cont_001",
  "date_range": {
    "start_date": "2023-11-01T00:00:00Z",
    "end_date": "2023-12-01T00:00:00Z",
    "days_back": 30
  },
  "timelogs": [
    {
      "id": "timelog_001_01",
      "version": 1,
      "uid": "timelog_uid_def456ghi789",
      "duration": 14400000,
      "duration_hours": 4.0,
      "time_start": 1701418800000,
      "time_end": 1701433200000,
      "type": "captured",
      "job_uid": "job_uid_abc123def456",
      "created_at": "2023-12-01T09:00:00Z"
    }
  ],
  "count": 5,
  "total_hours": 32.5,
  "note": "Query Pattern 4: Latest timelogs for contractor in time period"
}
```

---

### 7. Payments by Contractor

```
GET /api/payments/contractor/<contractor_id>/
GET /api/payments/contractor/<contractor_id>/?days=<number>
```

**Description**: Get all payment line items for a contractor in a time period (latest versions only)

**Parameters**:
- `contractor_id` (path): Contractor identifier
- `days` (query, optional): Number of days back to search (default: 30)

**Example Requests**:
```bash
# Last 30 days of payments
curl -X GET "http://localhost:8000/api/payments/contractor/cont_001/" \
  -H "Accept: application/json"

# Last 60 days of payments
curl -X GET "http://localhost:8000/api/payments/contractor/cont_001/?days=60" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "contractor_id": "cont_001",
  "date_range": {
    "start_date": "2023-11-01T00:00:00Z",
    "end_date": "2023-12-01T00:00:00Z",
    "days_back": 30
  },
  "payments": [
    {
      "id": "payment_0001",
      "version": 2,
      "uid": "paymentlineitem_uid_ghi789jkl012",
      "amount": "250.00",
      "status": "paid",
      "job_uid": "job_uid_abc123def456",
      "timelog_uid": "timelog_uid_def456ghi789",
      "payment_date": "2023-11-28T00:00:00Z",
      "created_at": "2023-11-25T10:00:00Z"
    }
  ],
  "count": 8,
  "total_amount": "1250.00",
  "note": "Query Pattern 3: Latest payment line items for contractor in time period"
}
```

---

### 8. Contractor Dashboard

```
GET /api/dashboard/contractor/<contractor_id>/
GET /api/dashboard/contractor/<contractor_id>/?days=<number>
```

**Description**: Combined dashboard showing all contractor data using SCD abstraction

**Parameters**:
- `contractor_id` (path): Contractor identifier
- `days` (query, optional): Number of days back for timelogs/payments (default: 30)

**Example Requests**:
```bash
# Dashboard for last 30 days
curl -X GET "http://localhost:8000/api/dashboard/contractor/cont_001/" \
  -H "Accept: application/json"

# Dashboard for last 14 days
curl -X GET "http://localhost:8000/api/dashboard/contractor/cont_001/?days=14" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "contractor_id": "cont_001",
  "period_days": 30,
  "summary": {
    "total_jobs": 3,
    "total_hours": 45.5,
    "total_amount": "2275.00"
  },
  "jobs": [
    {
      "id": "job_001",
      "version": 2,
      "title": "Software Engineer",
      "status": "active",
      "rate": "45.50"
    }
  ],
  "timelogs": [
    {
      "id": "timelog_001_01",
      "version": 1,
      "duration_hours": 4.0,
      "type": "captured"
    }
  ],
  "payments": [
    {
      "id": "payment_0001",
      "version": 2,
      "amount": "250.00",
      "status": "paid"
    }
  ],
  "note": "Comprehensive contractor dashboard using SCD abstraction"
}
```

---

### 9. Company Spending Report

```
GET /api/report/company/<company_id>/
GET /api/report/company/<company_id>/?month=<month>&year=<year>
```

**Description**: Company spending report using SCD abstraction

**Parameters**:
- `company_id` (path): Company identifier
- `month` (query, optional): Month number 1-12 (default: current month)
- `year` (query, optional): Year (default: current year)

**Example Requests**:
```bash
# Current month report
curl -X GET "http://localhost:8000/api/report/company/comp_001/" \
  -H "Accept: application/json"

# November 2023 report
curl -X GET "http://localhost:8000/api/report/company/comp_001/?month=11&year=2023" \
  -H "Accept: application/json"
```

**Example Response**:
```json
{
  "company_id": "comp_001",
  "report": {
    "month": 11,
    "year": 2023,
    "total_spending": "5500.00",
    "contractors": [
      {
        "contractor_id": "cont_001",
        "total_amount": "2275.00",
        "hours_worked": 45.5
      }
    ]
  },
  "note": "Company spending report using SCD abstraction"
}
```

---

## Test Data Setup

Before testing, create sample data by running:

```bash
cd /Users/amitdubey/Desktop/Personal/scd-work-trial
python manage.py create_sample_data --clear
```

This will create:
- **Companies**: `comp_001`, `comp_002`, `comp_003`
- **Contractors**: `cont_001`, `cont_002`, `cont_003`, `cont_004`, `cont_005`
- **Jobs**: `job_001`, `job_002`, etc. (with multiple versions)
- **Timelogs**: `timelog_001_01`, `timelog_001_02`, etc.
- **Payments**: `payment_0001`, `payment_0002`, etc.

## Quick Test Commands

### Start the Django Server
```bash
cd /Users/amitdubey/Desktop/Personal/scd-work-trial
python manage.py runserver
```

### Test All Endpoints
```bash
# 1. Root endpoint
curl "http://localhost:8000/api/"

# 2. Demo queries
curl "http://localhost:8000/api/demo/"

# 3. All jobs
curl "http://localhost:8000/api/jobs/"

# 4. Jobs by company
curl "http://localhost:8000/api/jobs/company/comp_001/"

# 5. Jobs by contractor
curl "http://localhost:8000/api/jobs/contractor/cont_001/"

# 6. Timelogs by contractor
curl "http://localhost:8000/api/timelogs/contractor/cont_001/"

# 7. Payments by contractor
curl "http://localhost:8000/api/payments/contractor/cont_001/"

# 8. Contractor dashboard
curl "http://localhost:8000/api/dashboard/contractor/cont_001/"

# 9. Company report
curl "http://localhost:8000/api/report/company/comp_001/"
```

## Error Responses

All endpoints return error responses in this format:
```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200 OK`: Successful request
- `500 Internal Server Error`: Server error (with error details in JSON)

## Key Features

1. **SCD Abstraction**: All data follows Slowly Changing Dimensions pattern
2. **Latest Version Filtering**: Automatically returns latest versions only
3. **Performance Optimized**: Efficient queries for large datasets
4. **Comprehensive Tracking**: Jobs, timelogs, and payments with full audit trail
5. **Query Pattern Examples**: Demonstrates 4 different SCD query patterns

## Data Models

### Job Fields
- `id`: Business identifier (same across versions)
- `version`: Version number
- `uid`: Unique identifier for this version
- `title`: Job title
- `status`: active, extended, paused, completed, cancelled
- `rate`: Hourly rate
- `company_id`: Associated company
- `contractor_id`: Associated contractor

### Timelog Fields
- `id`: Business identifier
- `version`: Version number
- `uid`: Unique identifier for this version
- `duration`: Duration in milliseconds
- `time_start`: Start timestamp (milliseconds)
- `time_end`: End timestamp (milliseconds)
- `type`: captured, adjusted, manual
- `job_uid`: References specific Job version

### PaymentLineItem Fields
- `id`: Business identifier
- `version`: Version number
- `uid`: Unique identifier for this version
- `amount`: Payment amount
- `status`: not-paid, paid, failed, pending, cancelled
- `payment_date`: When payment was made
- `job_uid`: References specific Job version
- `timelog_uid`: References specific Timelog version

---

You can now test all these endpoints with the provided examples!
