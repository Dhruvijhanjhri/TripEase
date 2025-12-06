# TripEase Django Setup Instructions

## Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Admin User

```bash
python manage.py createsuperuser
```

When prompted:
- Email: admin@tripease.com (or your email)
- Username: admin (or any username)
- Password: (choose a strong password)

### Step 4: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 5: Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Adding Sample Data

### 1. Add Airports (via Admin Panel)

1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Click "Airports" → "Add Airport"
4. Add airports like:
   - **BLR** - Kempegowda International Airport, Bengaluru
   - **DEL** - Indira Gandhi International Airport, Delhi
   - **BOM** - Chhatrapati Shivaji Maharaj International Airport, Mumbai
   - **CCU** - Netaji Subhas Chandra Bose International Airport, Kolkata
   - **MAA** - Chennai International Airport, Chennai
   - **HYD** - Rajiv Gandhi International Airport, Hyderabad

### 2. Add Flights (via Admin Panel)

1. Go to Admin Panel → "Flights" → "Add Flight"
2. Fill in details:
   - **Flight Number**: e.g., "AI-101"
   - **Airline**: e.g., "Air India"
   - **Source**: Select airport (e.g., BLR)
   - **Destination**: Select airport (e.g., DEL)
   - **Departure Time**: e.g., "2025-12-01 10:00:00"
   - **Arrival Time**: e.g., "2025-12-01 12:30:00"
   - **Duration Minutes**: e.g., 150
   - **Economy Price**: e.g., 5000
   - **Business Price**: e.g., 12000
   - **First Class Price**: e.g., 25000
   - **Total Seats**: e.g., 180
   - **Available Seats**: e.g., 180
   - **Is Non Stop**: Check if non-stop flight

### 3. Test the Application

1. **Sign Up**: Create a new user account
2. **Search Flights**: Use the search form on home page
3. **Book Flight**: Select a flight and complete booking
4. **Make Payment**: Complete payment (simulated)
5. **View Bookings**: Check "My Bookings" page

## Common Issues & Solutions

### Issue: "No module named 'django'"
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Issue: "Table doesn't exist"
**Solution**: Run migrations: `python manage.py migrate`

### Issue: Static files not loading
**Solution**: Run: `python manage.py collectstatic --noinput`

### Issue: Can't login with email
**Solution**: Make sure you're using the email you signed up with, not username

### Issue: "CSRF verification failed"
**Solution**: Make sure `{% csrf_token %}` is included in all forms

## File Structure

```
TripEase/
├── manage.py
├── requirements.txt
├── README.md
├── tripease/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/              # Home page
├── accounts/          # Authentication
├── flights/           # Flight management
├── bookings/          # Booking system
├── payments/          # Payment processing
├── contact/           # Contact form
├── templates/         # HTML templates
├── static/            # CSS, JS, images
└── media/             # User uploads
```

## Next Steps

1. ✅ Set up the project
2. ✅ Add airports and flights via admin
3. ✅ Test user registration and login
4. ✅ Test flight search and booking
5. ✅ Test payment flow
6. 🔄 Customize as needed
7. 🔄 Deploy to production

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Update `SECRET_KEY` (use environment variable)
3. Configure `ALLOWED_HOSTS`
4. Set up PostgreSQL database
5. Configure static file serving
6. Set up HTTPS
7. Configure email settings for password reset

---

**Happy Coding! 🚀**


