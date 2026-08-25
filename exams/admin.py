# FILE: exams/admin.py

from django.contrib import admin
from .models import Exam, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'marks')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'duration_minutes', 'pass_percentage', 'is_published', 'total_questions', 'total_marks', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'exam', 'correct_answer', 'marks')
    list_filter = ('exam', 'correct_answer')
    search_fields = ('question_text', 'exam__title')