from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    path('create/<int:flight_id>/', views.create_booking, name='create'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
]



