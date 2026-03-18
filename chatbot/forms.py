from django import forms
from .models import ChatMessage, ChatSession


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite sua mensagem aqui...',
                'required': True
            })
        }


class ChatSessionForm(forms.ModelForm):
    class Meta:
        model = ChatSession
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título da conversa...'
            })
        }
