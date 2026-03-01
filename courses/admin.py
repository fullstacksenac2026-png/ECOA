from django.contrib import admin
from .models import (
    Course, Enrollment, Teacher, VideoCourse, CourseMaterial, 
    TextContentCoursePage, Quiz, QuizAnswer, QuizQuestion, QuizResult,
    Category, Section, Lesson, Video, Comment, CommentLike, 
    UserLessonProgress, UserQuizAnswer
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'time', 'rating', 'students_count', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'students_count')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'price', 'time', 'image')
        }),
        ('Estatísticas', {
            'fields': ('rating', 'students_count')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'course__name')
    ordering = ('course', 'order')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('course', 'title', 'description', 'order')
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'lesson_type', 'duration_minutes', 'order')
    list_filter = ('lesson_type', 'section__course')
    search_fields = ('title', 'section__title')
    ordering = ('section', 'order')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('section', 'title', 'description', 'lesson_type')
        }),
        ('Configurações', {
            'fields': ('duration_minutes', 'order')
        }),
    )


class VideoInline(admin.StackedInline):
    model = Video
    extra = 0
    fields = ('video_url', 'transcript')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'video_url')
    search_fields = ('lesson__title',)
    fieldsets = (
        ('Informações do Vídeo', {
            'fields': ('lesson', 'video_url', 'transcript')
        }),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    list_filter = ('enrolled_at', 'course')
    search_fields = ('user__username', 'course__name')
    readonly_fields = ('enrolled_at',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'assigned_at')
    list_filter = ('assigned_at', 'course')
    search_fields = ('user__username', 'course__name')
    readonly_fields = ('assigned_at',)


@admin.register(VideoCourse)
class VideoCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'time')
    search_fields = ('title', 'course__name')


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__name')
    readonly_fields = ('created_at',)


@admin.register(TextContentCoursePage)
class TextContentCoursePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__name')
    readonly_fields = ('created_at',)


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1
    fields = ('text', 'question_type', 'points', 'order')


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 1
    fields = ('text', 'is_correct', 'order')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'passing_score', 'max_attempts', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'course__name')
    readonly_fields = ('created_at',)
    inlines = [QuizQuestionInline]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('course', 'lesson', 'title', 'description')
        }),
        ('Configurações', {
            'fields': ('passing_score', 'max_attempts')
        }),
    )


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz__course')
    search_fields = ('text', 'quiz__title')
    ordering = ('quiz', 'order')
    inlines = [QuizAnswerInline]


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz__course')
    search_fields = ('text', 'question__text')
    ordering = ('question', 'order')


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'percentage', 'passed', 'attempt_number', 'taken_at')
    list_filter = ('passed', 'quiz__course', 'taken_at')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('taken_at', 'taken_at')
    ordering = ('-taken_at',)


@admin.register(UserQuizAnswer)
class UserQuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_result', 'question', 'is_correct', 'points_earned')
    list_filter = ('is_correct', 'quiz_result__quiz__course')
    search_fields = ('question__text', 'quiz_result__user__username')
    readonly_fields = ('answered_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'likes_count', 'created_at')
    list_filter = ('created_at', 'course')
    search_fields = ('content', 'user__username', 'course__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'comment__content')
    readonly_fields = ('created_at',)


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'progress_percentage', 'started_at')
    list_filter = ('is_completed', 'started_at')
    search_fields = ('user__username', 'lesson__title')
    readonly_fields = ('started_at', 'completed_at')
