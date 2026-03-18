app_name = 'pictures'

from django.urls import path
from . import views

urlpatterns = [
    path('historic-pictures/', views.historic_pictures, name='historic-pictures'),
    path('details-picture/<int:picture_id>/', views.details_pictures, name='details-picture'),
    path('take-picture', views.take_picture, name='take-picture'),
    path('create-picture', views.create_picture, name="create-picture"),
    path('create-complaint/<int:picture_id>/', views.create_complaint, name="create-complaint"),
    path('update-picture/<int:picture_id>/', views.update_picture, name="update-picture"),
    path('delete-picture/<int:picture_id>/', views.delete_picture, name="delete-picture"),
    
    path('like-picture/<int:picture_id>/', views.like_picture, name='like-picture'),
    path('comment-picture/<int:picture_id>/', views.comment_picture, name='comment-picture'),
    path('reply-comment/<int:comment_id>/', views.reply_comment, name='reply-comment'),
    path('like-comment/<int:comment_id>/', views.like_comment, name='like-comment'),
    
    # API endpoints para IA
    path('api/verify-image/', views.verify_image_ai, name='verify-image-ai'),
    path('api/classify-image/', views.classify_image_api, name='classify-image-api'),
]