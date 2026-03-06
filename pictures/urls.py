app_name = 'pictures'

from django.urls import path
from . import views

urlpatterns = [
    path('historic-pictures/', views.historic_pictures, name='historic-pictures'),
    path('details-picture/<int:picture_id>/', views.details_pictures, name='details-picture'),
    path('take-picture', views.take_picture, name='take-picture'),
    path('create-picture', views.create_picture, name="create-picture"),
    path('update-picture/<int:picture_id>/', views.update_picture, name="update-picture"),
    path('delete-picture/<int:picture_id>/', views.delete_picture, name="delete-picture"),
]