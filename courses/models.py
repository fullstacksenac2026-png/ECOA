from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# ===================== MODELOS PRINCIPAIS =====================

class Category(models.Model):
    """Categoria de cursos"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.CharField(max_length=100, default='0 horas')
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    students_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ===================== ESTRUTURA DE AULAS =====================

class Section(models.Model):
    """Seção/Módulo do curso - agrupa lições"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.title} - {self.course.name}"


class Lesson(models.Model):
    """Lição dentro de uma seção"""
    LESSON_TYPES = [
        ('video', 'Vídeo'),
        ('text', 'Texto'),
        ('assignment', 'Tarefa'),
    ]
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='video')
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.title} - {self.section.title}"


class Video(models.Model):
    """Vídeo associado a uma lição"""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='video')
    video_url = models.URLField()
    transcript = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Video for {self.lesson.title}"


# ===================== MODELOS DE SUPORTE =====================

class Enrollment(models.Model):
    """Matrícula do usuário no curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.name}"
    

class Teacher(models.Model):
    """Professor do curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} teaches {self.course.name}"


class VideoCourse(models.Model):
    """Modelo legado de vídeos"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    video_url = models.URLField()
    time = models.CharField(max_length=100, default='0 min')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} for {self.course.name}"


class CourseMaterial(models.Model):
    """Material de curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    file_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.course.name}"


class TextContentCoursePage(models.Model):
    """Conteúdo textual de página do curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.course.name}"


class Certificate(models.Model):
    """Certificado de conclusão"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.user.username} in {self.course.name}"


# ===================== SISTEMA DE QUIZ =====================

class Quiz(models.Model):
    """Quiz do curso"""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    passing_score = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.course.name}"


class QuizQuestion(models.Model):
    """Pergunta do quiz"""
    QUESTION_TYPES = [
        ('multiple', 'Múltipla Escolha'),
        ('true_false', 'Verdadeiro/Falso'),
        ('short_answer', 'Resposta Curta'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple')
    order = models.PositiveIntegerField(default=0)
    points = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Question {self.order} for {self.quiz.title}"


class QuizAnswer(models.Model):
    """Alternativa de resposta do quiz"""
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Answer {self.order} for {self.question.text[:30]}"


class QuizResult(models.Model):
    """Resultado do quiz do usuário"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE, related_name='quiz_results')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    taken_at = models.DateTimeField(auto_now_add=True)
    time_taken_seconds = models.IntegerField(default=0)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.percentage}%)"


class UserQuizAnswer(models.Model):
    """Respostas do usuário para cada pergunta"""
    quiz_result = models.ForeignKey(QuizResult, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(QuizAnswer, on_delete=models.SET_NULL, null=True, blank=True)
    answer_text = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    points_earned = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_result.user.username}'s answer to {self.question.text[:30]}"


# ===================== COMENTÁRIOS E INTERAÇÕES =====================

class Comment(models.Model):
    """Comentários em video/aulas"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    content = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} commented on {self.course.name}"


class CommentLike(models.Model):
    """Likes em comentários"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes')
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"


# ===================== PROGRESSO DO USUÁRIO =====================

class UserLessonProgress(models.Model):
    """Rastreia o progresso do usuário em lições"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE, related_name='lesson_progress')
    is_completed = models.BooleanField(default=False)
    progress_percentage = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('lesson', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.progress_percentage}%)"


# ===================== MODELOS LEGADOS =====================

class Assignment(models.Model):
    """Tarefas/Assignments do curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.course.name}"


class View(models.Model):
    """Visualizações de curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} viewed {self.course.name}"


class Like(models.Model):
    """Curtidas em cursos/comentários"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.course.name}"


class Dislike(models.Model):
    """Descurtidas em cursos/comentários"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('authorization.User', on_delete=models.CASCADE)
    disliked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} disliked {self.course.name}"