from django.urls import path
from . import views, user_views
from . import exports

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("my-dashboard/", user_views.user_dashboard, name="user_dashboard"),
    path(
        "export/csv/",
        exports.export_csv,
        name="export_csv",
    ),
    path(
        "export/excel/",
        exports.export_excel,
        name="export_excel",
    ),
    path(
        "export/pdf/",
        exports.export_pdf,
        name="export_pdf",
    ),
    path(
        "analytics/bookings/",
        views.booking_trend,
        name="booking_trend",
    ),
    path(
        "analytics/revenue/",
        views.revenue_forecast,
        name="revenue_forecast",
    ),
]
