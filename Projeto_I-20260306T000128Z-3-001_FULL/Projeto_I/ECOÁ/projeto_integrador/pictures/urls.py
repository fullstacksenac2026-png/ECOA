from django.urls import path
from . import views

urlpatterns = [
    path('historic-pictures/', views.historic_pictures, name='historic-pictures'),
]