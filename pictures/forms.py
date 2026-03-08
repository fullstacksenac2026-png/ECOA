from django import forms
from .models import Complaint, Picture

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'content']
        labels = {
            'title': 'Tipo de Ocorrência',
            'content': 'Descrição do Problema'
        }
        widgets = {
            'title': forms.Select(attrs={
                'class': 'form-select form-select-lg shadow-sm',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control shadow-sm',
                'rows': 4,
                'placeholder': 'Descreva o que aconteceu neste local...',
                'required': True
            }),
        }

class PictureUpdateForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['title', 'content']
        labels = {
            'title': 'Título da Imagem',
            'content': 'Descrição Reduzida'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'content': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3}),
        }
