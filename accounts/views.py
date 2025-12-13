from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from .forms import SignUpForm, LoginForm, ProfileUpdateForm
from .models import User
import logging
import base64

logger = logging.getLogger(__name__)

# Try to import Supabase client, handle gracefully if not available
try:
    from .supabase_client import get_supabase_client, get_supabase_admin_client, SUPABASE_AVAILABLE
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase client not available. Authentication will use Django's default system.")
    
    def get_supabase_client():
        raise ImportError("Supabase is not available")
    
    def get_supabase_admin_client():
        raise ImportError("Supabase is not available")


def sync_user_to_supabase(django_user):
    """Sync Django user data to Supabase Auth user metadata using user_id"""
    if not SUPABASE_AVAILABLE or not django_user.user_id:
        return False
    
    try:
        supabase = get_supabase_admin_client()
        # Update user metadata in Supabase using user_id (UUID)
        supabase.auth.admin.update_user_by_id(
            str(django_user.user_id),
            {
                "user_metadata": {
                    "first_name": django_user.first_name or "",
                    "last_name": django_user.last_name or "",
                    "phone": django_user.phone or "",
                }
            }
        )
        return True
    except Exception as e:
        logger.error(f"Error syncing user to Supabase: {str(e)}")
        return False


def signup_view(request):
    """User registration view with Supabase integration"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                password = form.cleaned_data['password1']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone = form.cleaned_data['phone']
                profile_photo = form.cleaned_data.get('profile_photo')
                
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    logger.debug(f"Signup attempt with existing email: {email}")
                    messages.error(request, 'An account with this email already exists.')
                    return render(request, 'accounts/signup.html', {'form': form})
                
                supabase_user_id = None
                
                # Create user in Supabase Auth if available
                if SUPABASE_AVAILABLE:
                    try:
                        supabase = get_supabase_client()
                        auth_response = supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "first_name": first_name,
                                    "last_name": last_name,
                                    "phone": phone or "",
                                }
                            }
                        })
                        
                        if auth_response.user:
                            supabase_user_id = auth_response.user.id
                            logger.info(f"User created in Supabase: {email} with ID: {supabase_user_id}")
                    except Exception as e:
                        logger.warning(f"Supabase signup failed, falling back to Django: {str(e)}")
                        # Continue with Django-only signup if Supabase fails
                
                # Create Django User with proper password hashing
                django_user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,  # This will be hashed automatically
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    is_active=True,
                )
                
                # Set user_id from Supabase if available
                if supabase_user_id:
                    django_user.user_id = supabase_user_id
                
                # Update profile photo if provided
                if profile_photo:
                    django_user.profile_photo = profile_photo
                
                django_user.save()
                logger.debug(f"User created successfully: {email}")
                
                # Sync user data to Supabase after creation
                if SUPABASE_AVAILABLE and django_user.user_id:
                    try:
                        sync_user_to_supabase(django_user)
                    except Exception as e:
                        logger.warning(f"Failed to sync to Supabase: {str(e)}")
                
                # Don't auto-login, redirect to login page as requested
                messages.success(request, 'Account created successfully! Please log in to continue.')
                logger.info(f"User {email} signed up successfully")
                return redirect('accounts:login')  # Redirect to login as requested
                
            except Exception as e:
                logger.error(f"Error during signup: {str(e)}", exc_info=True)
                messages.error(request, f'Failed to create account. Please try again.')
                return render(request, 'accounts/signup.html', {'form': form})
        else:
            # Form is invalid, log errors for debugging
            logger.debug(f"Signup form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    logger.debug(f"  {field}: {error}")
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """User login view with Supabase integration"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']  # LoginForm uses 'username' field for email
            password = form.cleaned_data['password']
            
            logger.debug(f"Login attempt for email: {email}")
            
            # Try Supabase authentication first if available
            if SUPABASE_AVAILABLE:
                try:
                    supabase = get_supabase_client()
                    auth_response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if auth_response.user:
                        # Get or create Django User
                        supabase_user = auth_response.user
                        supabase_user_id = supabase_user.id
                        user_metadata = supabase_user.user_metadata or {}
                        
                        try:
                            django_user = User.objects.get(email=email)
                            # Update user_id if not set
                            if not django_user.user_id:
                                django_user.user_id = supabase_user_id
                            
                            # Sync data from Supabase to Django if metadata exists
                            if user_metadata:
                                django_user.first_name = user_metadata.get('first_name', django_user.first_name) or django_user.first_name
                                django_user.last_name = user_metadata.get('last_name', django_user.last_name) or django_user.last_name
                                django_user.phone = user_metadata.get('phone', django_user.phone) or django_user.phone
                            
                            django_user.save()
                        except User.DoesNotExist:
                            # Create Django user if it doesn't exist (for backward compatibility)
                            django_user = User.objects.create_user(
                                email=email,
                                username=email,
                                password=password,  # Set password for Django auth
                                first_name=user_metadata.get('first_name', ''),
                                last_name=user_metadata.get('last_name', ''),
                                phone=user_metadata.get('phone', ''),
                                user_id=supabase_user_id,
                                is_active=True,
                            )
                        
                        # Log in the Django user
                        login(request, django_user)
                        logger.info(f"User {email} logged in via Supabase")
                        messages.success(request, f'Welcome back, {django_user.first_name or django_user.username}!')
                        next_url = request.GET.get('next', 'core:home')
                        return redirect(next_url)
                except Exception as e:
                    logger.warning(f"Supabase login failed, trying Django auth: {str(e)}")
            
            # Fallback to Django authentication
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    logger.info(f"User {email} logged in via Django auth")
                    messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                    next_url = request.GET.get('next', 'core:home')
                    return redirect(next_url)
                else:
                    logger.warning(f"Login attempt for inactive user: {email}")
                    messages.error(request, 'Your account is inactive. Please contact support.')
            else:
                logger.warning(f"Failed login attempt for email: {email}")
                messages.error(request, 'Invalid email or password.')
        else:
            # Form is invalid, log errors for debugging
            logger.debug(f"Login form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    logger.debug(f"  {field}: {error}")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view with Supabase integration"""
    if SUPABASE_AVAILABLE:
        try:
            # Sign out from Supabase
            supabase = get_supabase_client()
            supabase.auth.sign_out()
        except Exception as e:
            logger.warning(f"Error during Supabase logout: {str(e)}")
    
    # Logout from Django
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('core:home')


@login_required
def profile_view(request):
    """User profile view for updating account information with Supabase sync"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Sync all user data to Supabase
            if SUPABASE_AVAILABLE:
                sync_user_to_supabase(user)
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


