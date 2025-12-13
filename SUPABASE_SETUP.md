# Supabase Integration Setup Guide

## Overview
This project integrates Supabase Auth for user authentication. User data is synced between Django and Supabase using email as the unique identifier.

## Configuration

### 1. Environment Variables
Set the following environment variables in your system or `.env` file:

```bash
# Required
SUPABASE_URL=https://cakngwyybeqlxdolbdqh.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Optional (for admin operations)
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### 2. Getting Your Supabase Keys

1. Go to your Supabase project dashboard: https://supabase.com/dashboard
2. Navigate to **Settings** → **API**
3. Copy the following:
   - **Project URL** → Use as `SUPABASE_URL`
   - **anon public** key → Use as `SUPABASE_ANON_KEY`
   - **service_role** key → Use as `SUPABASE_SERVICE_ROLE_KEY` (optional)

### 3. Installation

Install the Supabase Python client:
```bash
pip install supabase
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## How It Works

### User Signup
1. User signs up with email, password, first_name, last_name, phone
2. Account is created in Supabase Auth with metadata (first_name, last_name, phone)
3. Account is created in Django User model
4. Data is synced to Supabase user metadata

### User Login
1. User authenticates with Supabase using email and password
2. Django user is retrieved or created based on email
3. User metadata from Supabase is synced to Django
4. User is logged into Django session

### Profile Updates
1. User updates profile in Django
2. Changes are automatically synced to Supabase user metadata

## Data Synced to Supabase

Only essential user data is synced to Supabase Auth user metadata:
- `first_name`
- `last_name`
- `phone`

## Database Schema

The Django `accounts_user` table matches your Supabase database schema:
- `id` (primary key)
- `email` (unique)
- `username` (unique)
- `first_name`
- `last_name`
- `phone`
- `profile_photo`
- `id_document`
- `password`
- `is_active`
- `is_staff`
- `is_superuser`
- `date_joined`
- `last_login`
- `created_at`
- `updated_at`

**Note:** The `supabase_user_id` field has been removed. Users are linked by email address.

## Fallback Behavior

If Supabase is not configured or unavailable:
- The system falls back to Django's built-in authentication
- All functionality continues to work
- No errors are thrown

## Testing

1. Set your environment variables
2. Start the Django server: `python manage.py runserver`
3. Test signup: Create a new account
4. Test login: Log in with the created account
5. Check Supabase dashboard: Verify user appears in Authentication → Users

## Troubleshooting

### "Supabase package not installed"
```bash
pip install supabase
```

### "Supabase URL and ANON KEY must be set"
Make sure you've set the environment variables:
```bash
export SUPABASE_URL=https://cakngwyybeqlxdolbdqh.supabase.co
export SUPABASE_ANON_KEY=your-key-here
```

### User not found in Supabase
- Check if the user was created successfully during signup
- Verify the email matches in both systems
- Check Supabase dashboard for authentication logs

## Production Deployment

For production (e.g., Render.com):
1. Add environment variables in your hosting platform's dashboard
2. Set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and optionally `SUPABASE_SERVICE_ROLE_KEY`
3. The application will automatically use these values

