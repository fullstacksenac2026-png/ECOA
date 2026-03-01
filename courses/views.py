from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta
import json
import time

from .models import (
    Course, Enrollment, Teacher, VideoCourse, CourseMaterial, 
    TextContentCoursePage, Quiz, QuizAnswer, QuizQuestion, QuizResult,
    Category, Section, Lesson, Video, Comment, CommentLike, 
    UserLessonProgress, UserQuizAnswer
)
from django.core.paginator import Paginator

# Create your views here.
def list_courses_and_categories(request):
    category = Category.objects.all()
    course = Course.objects.all()

    paginator_course = Paginator(course, 10)
    page_number = request.GET.get('page')
    page_obj_course = paginator_course.get_page(page_number)

    paginator_category = Paginator(category, 10)
    page_number_category = request.GET.get('page_category')
    page_obj_category = paginator_category.get_page(page_number_category)
    
    return render(request, 'list-courses.html', {'categories': page_obj_category, 'courses': page_obj_course})


def course_detail(request, course_id):
    """Página inicial do curso com descrição geral"""
    course = get_object_or_404(Course, id=course_id)
    teachers = Teacher.objects.filter(course=course)
    sections = Section.objects.filter(course=course).prefetch_related('lessons')
    comments = Comment.objects.filter(course=course, parent_comment__isnull=True).select_related('user')
    
    # Verificar se o usuário está matriculado
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    # Calcular estatísticas
    total_lessons = Lesson.objects.filter(section__course=course).count()
    avg_rating = Comment.objects.filter(course=course).aggregate(Avg('likes_count'))['likes_count__avg'] or 0
    students_count = Enrollment.objects.filter(course=course).count()
    
    context = {
        'course': course,
        'teachers': teachers,
        'sections': sections,
        'comments': comments,
        'is_enrolled': is_enrolled,
        'total_lessons': total_lessons,
        'avg_rating': avg_rating,
        'students_count': students_count,
    }
    return render(request, 'course-detail.html', context)


def list_courses_by_category(request, category_id):
    """Return list of courses filtered by category if the relation exists.
    """
    categories = Category.objects.all()
    try:
        courses = Course.objects.filter(category_id=category_id)
    except Exception:
        courses = Course.objects.all()

    paginator_course = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj_course = paginator_course.get_page(page_number)

    paginator_category = Paginator(categories, 10)
    page_number_category = request.GET.get('page_category')
    page_obj_category = paginator_category.get_page(page_number_category)

    return render(request, 'list-courses-by-category.html', {
        'categories': page_obj_category,
        'courses': page_obj_course,
        'current_category_id': category_id,
    })


@login_required
def course_lessons_detail(request, course_id):
    """Página principal do curso com todas as seções e lições"""
    course = get_object_or_404(Course, id=course_id)
    
    # Verificar se o usuário está matriculado
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    sections = Section.objects.filter(course=course).prefetch_related('lessons')
    
    # Obter progresso do usuário
    total_lessons = Lesson.objects.filter(section__course=course).count()
    completed_lessons = UserLessonProgress.objects.filter(
        user=request.user, 
        lesson__section__course=course,
        is_completed=True
    ).count()
    
    progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    context = {
        'course': course,
        'sections': sections,
        'progress_percentage': int(progress_percentage),
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
    }
    return render(request, 'course-lessons-detail.html', context)


@login_required
def course_video(request, lesson_id):
    """Página de vídeo com comentários e transcrição"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course
    
    # Verificar se o usuário está matriculado
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Verificar se a lição tem vídeo
    video = get_object_or_404(Video, lesson=lesson)
    
    # Obter ou criar o progresso do usuário
    lesson_progress, created = UserLessonProgress.objects.get_or_create(
        lesson=lesson,
        user=request.user
    )
    
    # Atualizar progresso para 100% se não estava
    if lesson_progress.progress_percentage < 100:
        lesson_progress.progress_percentage = 100
        lesson_progress.save()
    
    # Obter comentários
    comments = Comment.objects.filter(lesson=lesson, parent_comment__isnull=True).select_related('user')
    
    # Obter próxima e lição anterior
    all_lessons = Lesson.objects.filter(section__course=course).order_by('section__order', 'order')
    lesson_list = list(all_lessons)
    current_index = lesson_list.index(lesson) if lesson in lesson_list else None
    
    previous_lesson = lesson_list[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = lesson_list[current_index + 1] if current_index and current_index < len(lesson_list) - 1 else None
    
    # Obter todos os comentários com seus likes
    for comment in comments:
        comment.user_liked = CommentLike.objects.filter(
            comment=comment,
            user=request.user
        ).exists() if request.user.is_authenticated else False
    
    # Obter seções e lições para sidebar
    sections = Section.objects.filter(course=course).prefetch_related('lessons')
    
    context = {
        'lesson': lesson,
        'course': course,
        'video': video,
        'comments': comments,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'sections': sections,
    }
    return render(request, 'course-video.html', context)


@login_required
@require_http_methods(["POST"])
def add_comment(request, lesson_id):
    """Adicionar comentário a uma lição"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course
    
    # Verificar se o usuário está matriculado
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
    
    parent_comment = None
    if parent_id:
        parent_comment = get_object_or_404(Comment, id=parent_id)
    
    comment = Comment.objects.create(
        lesson=lesson,
        course=course,
        user=request.user,
        content=content,
        parent_comment=parent_comment
    )
    
    return JsonResponse({
        'id': comment.id,
        'username': request.user.username,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%d/%m/%Y às %H:%M'),
        'is_reply': parent_comment is not None
    })


@login_required
@require_http_methods(["POST"])
def like_comment(request, comment_id):
    """Dar like em um comentário"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Verificar se o usuário já deu like
    like, created = CommentLike.objects.get_or_create(
        comment=comment,
        user=request.user
    )
    
    if not created:
        # Se já tinha like, remove
        like.delete()
        return JsonResponse({'liked': False, 'likes_count': comment.comment_likes.count()})
    
    # Atualizar contagem de likes do comentário
    comment.likes_count = comment.comment_likes.count()
    comment.save()
    
    return JsonResponse({'liked': True, 'likes_count': comment.likes_count})


@login_required
def course_quiz(request, quiz_id):
    """Página do quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    lesson = quiz.lesson
    
    # Verificar se o usuário está matriculado
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Verificar tentativas limitadas
    attempts = QuizResult.objects.filter(quiz=quiz, user=request.user).count()
    if attempts >= quiz.max_attempts:
        return redirect('courses:quiz-results', quiz_id=quiz.id)
    
    # Obter perguntas
    questions = QuizQuestion.objects.filter(quiz=quiz).prefetch_related('answers')
    
    if request.method == 'POST':
        # Processar respostas do quiz
        start_time = request.POST.get('start_time')
        
        # Calcular tempo decorrido
        if start_time:
            try:
                start = float(start_time)
                time_taken = int(time.time() - start)
            except:
                time_taken = 0
        else:
            time_taken = 0
        
        total_points = sum(q.points for q in questions)
        earned_points = 0
        quiz_result = QuizResult.objects.create(
            quiz=quiz,
            user=request.user,
            score=0,
            attempt_number=attempts + 1,
            time_taken_seconds=time_taken
        )
        
        # Processar cada resposta
        for question in questions:
            answer_key = f'question_{question.id}'
            
            if question.question_type in ['multiple', 'true_false']:
                selected_answer_id = request.POST.get(answer_key)
                selected_answer = None
                is_correct = False
                
                if selected_answer_id:
                    try:
                        selected_answer = QuizAnswer.objects.get(id=selected_answer_id, question=question)
                        is_correct = selected_answer.is_correct
                    except QuizAnswer.DoesNotExist:
                        pass
                
                if is_correct:
                    earned_points += question.points
                
                UserQuizAnswer.objects.create(
                    quiz_result=quiz_result,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct,
                    points_earned=question.points if is_correct else 0
                )
            
            elif question.question_type == 'short_answer':
                answer_text = request.POST.get(answer_key, '').strip()
                # Nota: Para respostas curtas, geralmente precisaría de validação manual
                # Este é um exemplo básico
                UserQuizAnswer.objects.create(
                    quiz_result=quiz_result,
                    question=question,
                    answer_text=answer_text,
                    is_correct=False,
                    points_earned=0
                )
        
        # Salvar resultado
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        quiz_result.score = earned_points
        quiz_result.percentage = percentage
        quiz_result.passed = percentage >= quiz.passing_score
        quiz_result.save()
        
        # Marcar lição como completa se passou
        if quiz_result.passed and lesson:
            lesson_progress, _ = UserLessonProgress.objects.get_or_create(
                lesson=lesson,
                user=request.user
            )
            lesson_progress.is_completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save()
        
        return redirect('courses:quiz-results', quiz_id=quiz.id, result_id=quiz_result.id)
    
    # Obter seções e lições para sidebar
    if lesson:
        sections = Section.objects.filter(course=course).prefetch_related('lessons')
    else:
        sections = []
    
    context = {
        'quiz': quiz,
        'course': course,
        'lesson': lesson,
        'questions': questions,
        'attempts': attempts,
        'max_attempts': quiz.max_attempts,
        'sections': sections,
    }
    return render(request, 'course-quiz.html', context)


@login_required
def quiz_results(request, quiz_id, result_id=None):
    """Página de resultados do quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    
    # Verificar se o usuário está matriculado
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Obter o último resultado do usuário ou o especificado
    if result_id:
        quiz_result = get_object_or_404(QuizResult, id=result_id, quiz=quiz, user=request.user)
    else:
        quiz_result = QuizResult.objects.filter(quiz=quiz, user=request.user).first()
        if not quiz_result:
            return redirect('courses:course-quiz', quiz_id=quiz.id)
    
    # Obter respostas do usuário
    user_answers = UserQuizAnswer.objects.filter(quiz_result=quiz_result).select_related('question', 'selected_answer')
    
    # Agrupar respostas por pergunta
    answers_by_question = {}
    for answer in user_answers:
        answers_by_question[answer.question.id] = answer
    
    # Obter todas as perguntas com respostas corretas
    questions = QuizQuestion.objects.filter(quiz=quiz).prefetch_related('answers')
    
    # Verificar se pode tentar novamente
    attempts = QuizResult.objects.filter(quiz=quiz, user=request.user).count()
    can_retry = attempts < quiz.max_attempts and not quiz_result.passed
    
    # Obter histórico de tentativas
    previous_attempts = QuizResult.objects.filter(quiz=quiz, user=request.user).order_by('-taken_at')
    
    # Obter seções e lições para sidebar
    lesson = quiz.lesson
    if lesson:
        sections = Section.objects.filter(course=course).prefetch_related('lessons')
    else:
        sections = []
    
    context = {
        'quiz': quiz,
        'quiz_result': quiz_result,
        'course': course,
        'lesson': lesson,
        'questions': questions,
        'answers_by_question': answers_by_question,
        'can_retry': can_retry,
        'previous_attempts': previous_attempts,
        'sections': sections,
    }
    return render(request, 'course-quiz-results.html', context)