app_name = 'forum'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_list, name='forum-list'),
    path('forum/post/<int:post_id>/', views.forum_post_detail, name='forum-post-detail'),
    path('forum/post/<int:post_id>/edit/', views.post_update, name='forum-post-edit'),
    path('forum/post/<int:post_id>/delete/', views.post_delete, name='forum-post-delete'),
    path('forum/post-create', views.post_create, name='post-create')
]