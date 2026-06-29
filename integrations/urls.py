from django.urls import path
from . import views

app_name = "integrations"

urlpatterns = [

    path(
        "track-flight/<str:booking_reference>/",
        views.track_booking_flight,
        name="track_booking_flight",
    ),

]