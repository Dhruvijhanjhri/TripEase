from django.urls import path
from . import views

app_name = "hotels"

urlpatterns = [
    path("", views.hotel_search, name="search"),
    path("detail/<int:hotel_id>/", views.hotel_detail, name="detail"),
    path("booking/<int:room_id>/", views.hotel_booking, name="booking"),
    path("payment/<int:booking_id>/", views.hotel_payment, name="payment"),
    path(
        "cancel-booking/<str:booking_reference>/",
        views.cancel_booking,
        name="cancel_booking",
    ),
    path(
        "booking/<str:booking_reference>/",
        views.hotel_booking_detail,
        name="booking_detail",
    ),
]
