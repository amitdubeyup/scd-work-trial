# SCD Work Trial Project

## Quick Info
- **Developer**: Amit Dubey ([GitHub](https://github.com/amitdubeyup))
- **Contact**: amitdubey8888@gmail.com
- **Username**: amitdubeyup
- **Repository**: https://github.com/amitdubeyup/scd-work-trial
- **Technology**: Django + Python
- **Database**: SQLite (development)
- **Purpose**: SCD (Slowly Changing Dimensions) abstraction layer

## Quick Start
```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

# Test SCD functionality
python manage.py check

# Run server
python manage.py runserver
```

## Key Files
- `scd_app/scd_manager.py` - Core SCD abstraction
- `scd_app/models.py` - SCD models (Job, Timelog, PaymentLineItem)
- `scd_app/query_examples.py` - The 4 required query patterns
- `scd_app/views.py` - REST API endpoints

## Status: ✅ COMPLETE