# FILE: results/admin.py

from django.contrib import admin
from .models import ExamAttempt, StudentAnswer


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_correct', 'marks_obtained')
    can_delete = False


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'total_marks', 'percentage', 'passed', 'status', 'started_at', 'submitted_at')
    list_filter = ('status', 'passed', 'exam', 'started_at')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('started_at',)
    inlines = [StudentAnswerInline]


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct', 'marks_obtained')
    list_filter = ('is_correct', 'selected_option')
    search_fields = ('attempt__student__username', 'question__question_text')