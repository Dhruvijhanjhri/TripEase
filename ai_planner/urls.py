from django.urls import path
from . import views

app_name = "ai_planner"

urlpatterns = [
    path("", views.planner_home, name="planner"),
    path("result/<int:trip_id>/", views.planner_result, name="result"),
    path("history/", views.planner_history, name="history"),
    path(
        "export/<int:trip_id>/",
        views.export_trip_pdf,
        name="export_pdf"
    ),
]