app_name = 'courses'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_courses_and_categories, name='list-courses-and-categories'),
    # view to show courses filtered by category
    path('courses/category/<int:category_id>/', views.list_courses_by_category, name='list-courses-by-category'),
    # course detail now only requires course_id
    path('courses/<int:course_id>/', views.course_detail, name='course-detail'),
    # Novas URLs para a estrutura Coursera
    path('courses/<int:course_id>/lessons/', views.course_lessons_detail, name='course-lessons'),
    path('lesson/<int:lesson_id>/video/', views.course_video, name='course-video'),
    path('lesson/<int:lesson_id>/comments/add/', views.add_comment, name='add-comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like-comment'),
    path('quiz/<int:quiz_id>/', views.course_quiz, name='course-quiz'),
    path('quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz-results'),
    path('quiz/<int:quiz_id>/results/<int:result_id>/', views.quiz_results, name='quiz-results-detail'),
    # payment/checkout
    path('courses/<int:course_id>/checkout/', views.course_checkout, name='course-checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('payment/pending/', views.payment_pending, name='payment_pending'),
]