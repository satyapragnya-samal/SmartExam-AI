# FILE: results/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('start/<int:exam_id>/', views.start_exam_view, name='start_exam'),
    path('take/<int:attempt_id>/', views.take_exam_view, name='take_exam'),
    path('result/<int:attempt_id>/', views.exam_result_detail_view, name='exam_result_detail'),
    path('result/<int:attempt_id>/certificate/', views.download_certificate_pdf_view, name='download_certificate'),
    path('result/<int:attempt_id>/ai-analysis/', views.ai_diagnostic_analysis_view, name='ai_diagnostic_analysis'),
    path('api/doubt-chat/', views.doubt_chat_api_view, name='doubt_chat_api'),
    path('my-results/', views.student_results_view, name='student_results'),
]