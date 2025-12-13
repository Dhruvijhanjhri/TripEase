"""
Supabase client utility for authentication and database operations
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Try to import supabase, but handle if it's not installed
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase package not installed. Install it with: pip install supabase")
    Client = None

def get_supabase_client():
    """Get Supabase client instance"""
    if not SUPABASE_AVAILABLE:
        raise ImportError("Supabase package is not installed. Install it with: pip install supabase")
    
    try:
        supabase_url = settings.SUPABASE_URL
        supabase_key = settings.SUPABASE_ANON_KEY
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase URL and ANON KEY must be set in environment variables. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment."
            )
        
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Error creating Supabase client: {str(e)}")
        raise

def get_supabase_admin_client():
    """Get Supabase admin client with service role key for server-side operations"""
    if not SUPABASE_AVAILABLE:
        raise ImportError("Supabase package is not installed. Install it with: pip install supabase")
    
    try:
        supabase_url = settings.SUPABASE_URL
        # Prefer service role key, fallback to anon key if not available
        supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase URL and key must be set. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY) in your environment."
            )
        
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Error creating Supabase admin client: {str(e)}")
        raise

