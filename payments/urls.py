from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path(
        '<int:booking_id>/',
        views.payment_view,
        name='payment'
    ),

    path(
        'success/<int:booking_id>/',
        views.payment_success,
        name='success'
    ),
]