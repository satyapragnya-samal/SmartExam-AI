# FILE: exams/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        help_text="Duration of the exam in minutes",
        validators=[MinValueValidator(1)]
    )
    pass_percentage = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Minimum percentage required to pass"
    )
    is_published = models.BooleanField(
        default=False,
        help_text="Designates whether students can see and attempt this exam."
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_exams',
        limit_choices_to={'profile__role': 'teacher'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_marks(self):
        return sum(q.marks for q in self.questions.all())


class Question(models.Model):
    ANSWER_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    option_a = models.CharField(max_length=255, verbose_name="Option A")
    option_b = models.CharField(max_length=255, verbose_name="Option B")
    option_c = models.CharField(max_length=255, verbose_name="Option C")
    option_d = models.CharField(max_length=255, verbose_name="Option D")
    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        help_text="Select the correct option (A, B, C, or D)"
    )
    marks = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.exam.title} - Q: {self.question_text[:50]}..."