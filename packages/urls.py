from django.urls import path
from . import views

app_name = "packages"

urlpatterns = [

    path(
        "",
        views.package_search,
        name="search"
    ),

    path(
        "detail/<int:package_id>/",
        views.package_detail,
        name="detail"
    ),

    path(
        "book/<int:package_id>/",
        views.package_booking,
        name="book"
    ),

    path(
        "success/<int:booking_id>/",
        views.booking_success,
        name="booking_success"
    ),

    path(
        'booking/<str:booking_reference>/',
        views.package_booking_detail,
        name='booking_detail'
    ),

    path(
        "cancel-booking/<str:booking_reference>/",
        views.cancel_booking,
        name="cancel_booking",
    ),
    
    ]