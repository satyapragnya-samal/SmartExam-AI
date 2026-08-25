# FILE: results/models.py

from django.db import models
from django.contrib.auth.models import User
from exams.models import Exam, Question


class ExamAttempt(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('disqualified', 'Disqualified (Cheat Detected)'),
        ('timed_out', 'Timed Out'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_attempts',
        limit_choices_to={'profile__role': 'student'}
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    score = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    passed = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='in_progress')
    warning_count = models.PositiveIntegerField(default=0, help_text="Number of proctoring violations recorded")
    is_disqualified = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} ({self.status})"

    def calculate_final_score(self):
        """Calculates total marks, percentage, and pass/fail status on the server."""
        total = self.exam.total_marks
        earned = sum(ans.marks_obtained for ans in self.answers.all())
        self.total_marks = total
        self.score = earned
        self.percentage = (earned / total * 100) if total > 0 else 0
        self.passed = self.percentage >= self.exam.pass_percentage
        
        if self.is_disqualified:
            self.status = 'disqualified'
            self.passed = False
        else:
            self.status = 'completed'
            
        self.save()


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers'
    )
    selected_option = models.CharField(
        max_length=1,
        choices=Question.ANSWER_CHOICES,
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"Attempt {self.attempt.id} - Q: {self.question.id} ({self.selected_option})"