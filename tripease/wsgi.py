"""
WSGI config for TripEase project.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

path = '/home/dhruvijhanjhrinew/TripEase'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tripease.settings')

application = get_wsgi_application()


