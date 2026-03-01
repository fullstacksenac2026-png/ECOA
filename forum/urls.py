app_name = 'forum'
from django.urls import path
from . import views

urlpatterns = [
    path('forum/', views.forum_list, name='forum-list'),
]