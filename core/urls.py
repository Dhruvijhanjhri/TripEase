from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),

    # packages
    path('packages/', views.packages_view, name='packages'),
    path(
        'packages/<int:package_id>/',
        views.package_detail,
        name='package_detail'
    ),
]