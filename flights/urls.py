from django.urls import path
from . import views

app_name = "flights"

urlpatterns = [
    path("search/", views.flight_search, name="search"),

    # NEW
    path("flight/<int:flight_id>/", views.flight_detail, name="flight_detail"),
]