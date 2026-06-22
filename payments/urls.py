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

    path(
        'package/<int:booking_id>/',
        views.package_payment_view,
        name='package_payment'
    ),

    path(
        'package/success/<int:booking_id>/',
        views.package_payment_success,
        name='package_success'
    ),
]