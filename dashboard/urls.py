from django.urls import path
from . import views, user_views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('my-dashboard/', user_views.user_dashboard, name='user_dashboard'),
]