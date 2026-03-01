from django import forms
from .models import Comment, Enrollment, Quiz, QuizResult, Course


class CommentForm(forms.ModelForm):
    """Formulário para criar comentários em aulas"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Deixe seu comentário ou dúvida...',
                'rows': 3,
                'maxlength': 500,
            })
        }
        labels = {
            'content': 'Seu Comentário',
        }


class EnrollmentForm(forms.Form):
    """Formulário para se inscrever em um curso"""
    
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Aceito os termos e condições do curso'
    )
    
    def __init__(self, course=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.course = course


class QuizAnswerForm(forms.Form):
    """Formulário dinâmico para respostas de quiz"""
    
    def __init__(self, quiz=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if quiz:
            from .models import QuizQuestion
            questions = QuizQuestion.objects.filter(quiz=quiz)
            
            for question in questions:
                if question.question_type == 'multiple':
                    choices = [(answer.id, answer.text) for answer in question.answers.all()]
                    self.fields[f'question_{question.id}'] = forms.ChoiceField(
                        choices=[('', '-- Selecione uma opção --')] + choices,
                        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                        label=question.text,
                        required=False
                    )
                
                elif question.question_type == 'true_false':
                    choices = [(answer.id, answer.text) for answer in question.answers.all()]
                    self.fields[f'question_{question.id}'] = forms.ChoiceField(
                        choices=[('', '-- Selecione --')] + choices,
                        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                        label=question.text,
                        required=False
                    )
                
                elif question.question_type == 'short_answer':
                    self.fields[f'question_{question.id}'] = forms.CharField(
                        widget=forms.Textarea(attrs={
                            'class': 'form-control',
                            'placeholder': 'Digite sua resposta aqui...',
                            'rows': 3,
                        }),
                        label=question.text,
                        required=False
                    )


class CourseSearchForm(forms.Form):
    """Formulário para buscar cursos"""
    
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar cursos...',
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=None,  # Será preenchido pela view
        required=False,
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Preço mínimo',
            'step': '0.01',
        })
    )
    
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Preço máximo',
            'step': '0.01',
        })
    )
    
    ordering = forms.ChoiceField(
        choices=[
            ('name', 'Nome (A-Z)'),
            ('-created_at', 'Mais Recentes'),
            ('price', 'Preço (Menor)'),
            ('-price', 'Preço (Maior)'),
            ('-rating', 'Melhor Avaliação'),
        ],
        required=False,
        initial='name',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class CourseForm(forms.ModelForm):
    """Formulário para criar e editar cursos com upload de imagem"""
    
    class Meta:
        model = Course
        fields = ['name', 'description', 'price', 'time', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do curso',
                'maxlength': 100,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do curso',
                'rows': 5,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 40 horas',
                'maxlength': 100,
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
        labels = {
            'name': 'Nome do Curso',
            'description': 'Descrição',
            'price': 'Preço',
            'time': 'Duração',
            'image': 'Imagem de Capa',
        }
        help_texts = {
            'image': 'Selecione uma imagem para a capa do curso (PNG, JPG, JPEG)',
        }