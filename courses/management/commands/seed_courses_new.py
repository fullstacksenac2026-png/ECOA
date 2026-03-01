from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import (
    Category, Course, Section, Lesson, Video, Quiz, 
    QuizQuestion, QuizAnswer, Teacher
)
from authorization.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Popula dados de exemplo para courses'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando seed de dados...'))

        # Criar categorias
        categories = []
        category_names = ['Programação', 'Web Design', 'Data Science', 'Marketing Digital', 'Python']
        
        for name in category_names:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': f'Cursos de {name} para iniciantes e avançados'}
            )
            categories.append(cat)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Categoria "{name}" criada'))

        # Criar usuário professor
        teacher_user, created = User.objects.get_or_create(
            username='professor',
            defaults={
                'email': 'professor@example.com',
                'is_staff': False,
            }
        )
        if created:
            teacher_user.set_password('senha123')
            teacher_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Usuário professor criado'))

        # Criar um curso exemplo
        course, created = Course.objects.get_or_create(
            name='Python para Iniciantes',
            defaults={
                'description': 'Aprenda Python do zero com exemplos práticos e projetos reais',
                'price': Decimal('99.90'),
                'time': '40 horas',
                'rating': Decimal('4.8'),
                'students_count': 1523,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Curso "Python para Iniciantes" criado'))

            # Criar professor para o curso
            Teacher.objects.create(user=teacher_user, course=course)

            # Criar seções
            sections_data = [
                {
                    'title': 'Introdução ao Python',
                    'lessons': [
                        {
                            'title': 'Bem-vindo ao curso',
                            'duration': 5,
                            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
                        },
                        {
                            'title': 'Instalando Python e Ferramentas',
                            'duration': 15,
                            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
                        },
                        {
                            'title': 'Seu Primeiro Programa',
                            'duration': 10,
                            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
                        }
                    ]
                },
                {
                    'title': 'Los Fundamentos',
                    'lessons': [
                        {
                            'title': 'Variáveis e Tipos de Dados',
                            'duration': 20,
                            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
                        },
                        {
                            'title': 'Operadores em Python',
                            'duration': 15,
                            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
                        }
                    ]
                }
            ]

            for section_order, section_data in enumerate(sections_data):
                section, _ = Section.objects.get_or_create(
                    course=course,
                    title=section_data['title'],
                    defaults={'order': section_order}
                )
                
                for lesson_order, lesson_data in enumerate(section_data['lessons']):
                    lesson, lesson_created = Lesson.objects.get_or_create(
                        section=section,
                        title=lesson_data['title'],
                        defaults={
                            'description': f'Aprenda sobre {lesson_data["title"]}',
                            'lesson_type': 'video',
                            'duration_minutes': lesson_data['duration'],
                            'order': lesson_order
                        }
                    )
                    
                    if lesson_created:
                        # Criar vídeo para a lição
                        Video.objects.create(
                            lesson=lesson,
                            video_url=lesson_data['video_url'],
                            transcript='Transcrição do vídeo sobre ' + lesson_data['title']
                        )
                        
                        if lesson_order == len(section_data['lessons']) - 1:
                            # Criar quiz para a última lição da seção
                            quiz, _ = Quiz.objects.get_or_create(
                                course=course,
                                lesson=lesson,
                                title=f'Quiz - {section_data["title"]}',
                                defaults={
                                    'passing_score': 70,
                                    'max_attempts': 3,
                                    'description': f'Teste seus conhecimentos sobre {section_data["title"]}'
                                }
                            )
                            
                            # Criar perguntas do quiz
                            if quiz.questions.count() == 0:
                                question1, _ = QuizQuestion.objects.get_or_create(
                                    quiz=quiz,
                                    text='Qual é a extensão padrão de um arquivo Python?',
                                    defaults={
                                        'question_type': 'multiple',
                                        'order': 0,
                                        'points': 1
                                    }
                                )
                                
                                QuizAnswer.objects.get_or_create(
                                    question=question1,
                                    text='.py',
                                    defaults={'is_correct': True, 'order': 0}
                                )
                                QuizAnswer.objects.get_or_create(
                                    question=question1,
                                    text='.python',
                                    defaults={'is_correct': False, 'order': 1}
                                )
                                QuizAnswer.objects.get_or_create(
                                    question=question1,
                                    text='.p',
                                    defaults={'is_correct': False, 'order': 2}
                                )

        self.stdout.write(self.style.SUCCESS('✓ Seed de dados concluído com sucesso!'))
