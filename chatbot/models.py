from django.db import models
from authorization.models import User


class ChatSession(models.Model):
    """Sessão de chat entre usuário e IA"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default='Nova Conversa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Sessão de Chat'
        verbose_name_plural = 'Sessões de Chat'
    
    def __str__(self):
        return f"{self.user.email} - {self.title} ({self.created_at.strftime('%d/%m/%Y')})"


class ChatMessage(models.Model):
    """Mensagem em uma sessão de chat"""
    ROLE_CHOICES = [
        ('user', 'Usuário'),
        ('assistant', 'Assistente'),
        ('system', 'Sistema'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}..."
