from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<int:booking_id>/', views.payment_view, name='payment'),
    path('<int:booking_id>/success/', views.payment_success, name='success'),
]

