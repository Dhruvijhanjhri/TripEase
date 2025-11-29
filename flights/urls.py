from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('search/', views.flight_search, name='search'),
    path('<int:flight_id>/', views.flight_detail, name='detail'),
]

