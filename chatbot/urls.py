from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Chat views
    path('', views.chatbot_list, name='list'),
    path('novo/', views.create_chat, name='create'),
    path('sessao/<int:session_id>/', views.chat_detail, name='detail'),
    path('sessao/<int:session_id>/enviar/', views.send_message, name='send_message'),
    path('sessao/<int:session_id>/deletar/', views.delete_chat, name='delete'),
    
    # API endpoints
    path('api/enviar/', views.api_send_message, name='api_send_message'),
]
