from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('hotels/', views.hotels_search, name='hotels_search'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('packages/', views.packages_view, name='packages'),
    path('packages/<int:package_id>/', views.package_detail, name='package_detail'),
]


