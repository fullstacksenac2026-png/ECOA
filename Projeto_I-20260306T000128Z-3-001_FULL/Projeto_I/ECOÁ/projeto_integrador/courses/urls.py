from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.list_courses, name='list-courses')
]