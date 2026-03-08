from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('picture/<int:picture_id>/', views.report_picture, name='report_picture'),
    path('comment/<int:comment_id>/', views.report_comment, name='report_comment'),
    path('forum/post/<int:post_id>/', views.report_forum_post, name='report_forum_post'),
    path('forum/comment/<int:comment_id>/', views.report_forum_comment, name='report_forum_comment'),
]
