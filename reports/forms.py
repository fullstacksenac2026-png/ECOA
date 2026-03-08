from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select shadow-sm', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 3, 'placeholder': 'Mais informações...'}),
        }
        labels = {
            'reason': 'Motivo da Denúncia',
            'description': 'Detalhes (Opcional)'
        }
