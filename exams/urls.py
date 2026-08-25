# FILE: exams/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('list/', views.exam_list_teacher_view, name='exam_list_teacher'),
    path('available/', views.available_exams_view, name='available_exams'),
    path('create/', views.exam_create_view, name='exam_create'),
    path('<int:exam_id>/', views.exam_detail_view, name='exam_detail'),
    path('<int:exam_id>/edit/', views.exam_edit_view, name='exam_edit'),
    path('<int:exam_id>/delete/', views.exam_delete_view, name='exam_delete'),
    path('<int:exam_id>/publish/', views.exam_toggle_publish_view, name='exam_toggle_publish'),
    path('<int:exam_id>/question/add/', views.question_create_view, name='question_create'),
    path('<int:exam_id>/question/ai-generate/', views.ai_generate_questions_view, name='ai_generate_questions'),
    path('question/<int:question_id>/delete/', views.question_delete_view, name='question_delete'),
]