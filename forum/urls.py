app_name = 'forum'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_list, name='forum-list'),
    path('forum/post/<int:post_id>/', views.forum_post_detail, name='forum-post-detail'),
    path('forum/post-create', views.post_create, name='post-create')
]