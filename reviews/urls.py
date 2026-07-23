from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("hotel/<int:hotel_id>/add/", views.add_hotel_review, name="add_hotel_review"),
    path(
        "package/<int:package_id>/add/",
        views.add_package_review,
        name="add_package_review",
    ),
    path(
        "flight/<int:flight_id>/add/", views.add_flight_review, name="add_flight_review"
    ),
]
