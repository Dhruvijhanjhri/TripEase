# TripEase - Full-Stack Flight Booking Platform

TripEase is a comprehensive flight booking platform built with Django, featuring secure authentication, flight search, booking management, and payment processing.

## Features

✅ **User Authentication**
- Sign up with email, phone, and password
- Secure login/logout
- Password reset functionality
- User profiles with photo and ID document upload

✅ **Flight Search & Booking**
- Search flights by source, destination, and date
- Filter by cabin class (Economy, Business, First Class)
- Real-time seat availability
- Transparent pricing breakdown
- Booking management

✅ **Payment Processing**
- Multiple payment methods (UPI, Card, Net Banking)
- Simulated payment gateway
- Payment history tracking

✅ **Contact System**
- Contact form with file attachment support
- Admin panel for managing inquiries

✅ **Admin Panel**
- Manage airports, flights, bookings
- View and respond to contact messages
- User management

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (minimal, UI only)
- **Authentication**: Django Authentication System

## Project Structure

```
TripEase/
├── manage.py
├── tripease/          # Main project settings
├── core/              # Home page
├── accounts/          # Authentication & user management
├── flights/           # Flight search & management
├── bookings/          # Booking flow
├── payments/          # Payment processing
├── contact/           # Contact form
├── templates/         # Django templates
├── static/           # Static files (CSS, images)
└── media/            # User uploads
```

## Installation & Setup

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### 2. Clone/Download the Project

```bash
cd "D:\christ college\sem 2\full stack\final project"
```

### 3. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Admin Panel

Access the admin panel at `http://127.0.0.1:8000/admin/`

Login with the superuser credentials created in step 6.

## Adding Sample Data

### Add Airports

1. Go to Admin Panel → Airports
2. Click "Add Airport"
3. Fill in:
   - Code: e.g., "BLR" (IATA code)
   - Name: e.g., "Kempegowda International Airport"
   - City: e.g., "Bengaluru"
   - Country: e.g., "India"

### Add Flights

1. Go to Admin Panel → Flights
2. Click "Add Flight"
3. Fill in flight details:
   - Flight Number: e.g., "AI-101"
   - Airline: e.g., "Air India"
   - Source & Destination: Select airports
   - Departure & Arrival times
   - Prices for each cabin class
   - Total and available seats

## Usage Guide

### For Users

1. **Sign Up**: Create an account with email and password
2. **Search Flights**: Use the search form on the home page
3. **Select Flight**: Choose from available flights
4. **Enter Passenger Details**: Fill in passenger information
5. **Make Payment**: Complete payment using preferred method
6. **View Bookings**: Check booking status in "My Bookings"

### For Admins

1. **Manage Airports**: Add/Edit airports
2. **Manage Flights**: Create and update flight schedules
3. **View Bookings**: Monitor all bookings
4. **Contact Management**: Respond to user inquiries

## Production Deployment

### Database Configuration

For production, update `settings.py` to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### Environment Variables

Set these environment variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Your domain name
- Database credentials (if using PostgreSQL)

### Security Checklist

- [ ] Set `DEBUG = False`
- [ ] Update `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use HTTPS
- [ ] Set up proper database backups
- [ ] Configure email settings for password reset

## File Structure Details

- **Models**: Database models for User, Airport, Flight, Booking, Payment, Contact
- **Views**: Business logic and request handling
- **Forms**: Form validation and user input handling
- **Templates**: HTML templates with Django template language
- **Static Files**: CSS, JavaScript, images
- **Admin**: Django admin configurations

## Notes

- Payment processing is **simulated** for demonstration purposes
- For production, integrate with real payment gateways (Razorpay, Stripe, etc.)
- File uploads are stored in the `media/` directory
- Static files are served from `static/` directory

## Support

For issues or questions, contact: support@tripease.example

## License

This project is for educational purposes.

---

**Built with ❤️ using Django**

