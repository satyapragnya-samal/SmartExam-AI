# FILE: exams/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import teacher_required, student_required
from .models import Exam, Question
from .forms import ExamForm, QuestionForm
from results.models import ExamAttempt
from .ai_service import generate_mcqs_with_ai


@login_required
@teacher_required
def teacher_dashboard_view(request):
    exams = Exam.objects.filter(created_by=request.user)
    total_exams = exams.count()
    published_exams = exams.filter(is_published=True).count()
    total_questions = Question.objects.filter(exam__created_by=request.user).count()

    recent_attempts = ExamAttempt.objects.filter(
        exam__created_by=request.user
    ).exclude(status='in_progress').select_related('student', 'exam').order_by('-started_at')[:10]

    context = {
        'total_exams': total_exams,
        'published_exams': published_exams,
        'total_questions': total_questions,
        'total_attempts': ExamAttempt.objects.filter(exam__created_by=request.user).exclude(status='in_progress').count(),
        'recent_attempts': recent_attempts,
    }
    return render(request, 'exams/teacher_dashboard.html', context)


@login_required
@student_required
def student_dashboard_view(request):
    available_exams = Exam.objects.filter(is_published=True)
    my_attempts = ExamAttempt.objects.filter(student=request.user).exclude(status='in_progress')

    total_attempted = my_attempts.count()
    passed_count = my_attempts.filter(passed=True).count()

    context = {
        'available_exams': available_exams[:6],
        'total_attempted': total_attempted,
        'passed_count': passed_count,
    }
    return render(request, 'exams/student_dashboard.html', context)


@login_required
@teacher_required
def exam_list_teacher_view(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'exams/exam_list_teacher.html', {'exams': exams})


@login_required
@student_required
def available_exams_view(request):
    exams = Exam.objects.filter(is_published=True)
    
    # Query IDs of exams already completed by the student
    completed_exam_ids = list(
        ExamAttempt.objects.filter(
            student=request.user
        ).exclude(status='in_progress').values_list('exam_id', flat=True)
    )

    context = {
        'exams': exams,
        'completed_exam_ids': completed_exam_ids,
    }
    return render(request, 'exams/available_exams.html', context)


@login_required
@teacher_required
def exam_create_view(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, f"Exam '{exam.title}' created successfully!")
            return redirect('exam_detail', exam_id=exam.id)
    else:
        form = ExamForm()
    return render(request, 'exams/exam_form.html', {'form': form, 'title': 'Create Exam'})


@login_required
@teacher_required
def exam_detail_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all()
    return render(request, 'exams/exam_detail.html', {'exam': exam, 'questions': questions})


@login_required
@teacher_required
def exam_edit_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f"Exam '{exam.title}' updated successfully!")
            return redirect('exam_detail', exam_id=exam.id)
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/exam_form.html', {'form': form, 'title': 'Edit Exam'})


@login_required
@teacher_required
def exam_delete_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        exam_title = exam.title
        exam.delete()
        messages.success(request, f"Exam '{exam_title}' has been deleted.")
        return redirect('exam_list_teacher')
    return render(request, 'exams/exam_confirm_delete.html', {'exam': exam})


@login_required
@teacher_required
def exam_toggle_publish_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if not exam.is_published and exam.questions.count() == 0:
        messages.error(request, "Cannot publish an exam with no questions. Please add questions first.")
        return redirect('exam_detail', exam_id=exam.id)
    
    exam.is_published = not exam.is_published
    exam.save()
    status_str = "published and is now live for students" if exam.is_published else "unpublished (saved as draft)"
    messages.success(request, f"Exam '{exam.title}' has been {status_str}.")
    return redirect('exam_detail', exam_id=exam.id)


@login_required
@teacher_required
def question_create_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            messages.success(request, "Question added successfully!")
            return redirect('exam_detail', exam_id=exam.id)
    else:
        form = QuestionForm()
    return render(request, 'exams/question_form.html', {'form': form, 'exam': exam})


@login_required
@teacher_required
def ai_generate_questions_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        count = int(request.POST.get('count', 5))
        difficulty = request.POST.get('difficulty', 'medium')
        marks_per_q = int(request.POST.get('marks', 1))

        if not topic:
            messages.error(request, "Please enter a topic for question generation.")
            return redirect('ai_generate_questions', exam_id=exam.id)

        mcqs = generate_mcqs_with_ai(topic=topic, count=count, difficulty=difficulty, marks=marks_per_q)

        if not mcqs:
            messages.error(request, "AI generation failed. Please verify your GEMINI_API_KEY in the .env file.")
            return redirect('ai_generate_questions', exam_id=exam.id)

        created_count = 0
        for item in mcqs:
            Question.objects.create(
                exam=exam,
                question_text=item.get('question_text'),
                option_a=item.get('option_a'),
                option_b=item.get('option_b'),
                option_c=item.get('option_c'),
                option_d=item.get('option_d'),
                correct_answer=item.get('correct_answer'),
                marks=item.get('marks', marks_per_q)
            )
            created_count += 1

        messages.success(request, f"✨ Successfully generated and added {created_count} AI questions to '{exam.title}'!")
        return redirect('exam_detail', exam_id=exam.id)

    return render(request, 'exams/ai_generate_questions.html', {'exam': exam})


@login_required
@teacher_required
def question_delete_view(request, question_id):
    question = get_object_or_404(Question, id=question_id, exam__created_by=request.user)
    exam_id = question.exam.id
    question.delete()
    messages.success(request, "Question deleted successfully.")
    return redirect('exam_detail', exam_id=exam_id)