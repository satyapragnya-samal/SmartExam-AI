# FILE: exams/forms.py

from django import forms
from .models import Exam, Question


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'duration_minutes', 'pass_percentage', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python Fundamentals'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief overview of the exam syllabus'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'pass_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'is_published': forms.CheckboxInput(attrs={'style': 'width: auto; margin-top: 0.3rem;'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'marks']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter the question text here...'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}),
            'correct_answer': forms.Select(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }