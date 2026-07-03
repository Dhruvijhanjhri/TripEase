from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [

    path(
        "",
        views.booking_list,
        name="list"
    ),

    path(
        "create/<int:flight_id>/",
        views.create_booking,
        name="create"
    ),

    path(
        "detail/<str:booking_reference>/",
        views.booking_detail,
        name="detail"
    ),

    path(
        "cancel/<str:booking_reference>/",
        views.cancel_booking,
        name="cancel"
    ),

    path(
        "check-in/confirm/<str:booking_reference>/",
        views.check_in_confirm,
        name="check_in_confirm",
    ),

    path(
        "check-in/<str:booking_reference>/",
        views.check_in,
        name="check_in",
    ),

    path(
        "select-seats/<str:booking_reference>/",
        views.select_seats,
        name="select_seats",
    ),

    path(
        "boarding-pass/<str:booking_reference>/",
        views.download_boarding_pass,
        name="download_boarding_pass",
    ),

]