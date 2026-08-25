# FILE: results/views.py

import io
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from accounts.decorators import student_required
from exams.models import Exam, Question
from .models import ExamAttempt, StudentAnswer
from exams.ai_service import generate_student_diagnostic, get_doubt_bot_response


@login_required
@student_required
def start_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)

    if exam.questions.count() == 0:
        messages.error(request, "This exam does not have any questions yet.")
        return redirect('available_exams')

    # Security check: Block if already attempted / disqualified
    completed_attempt = ExamAttempt.objects.filter(
        student=request.user,
        exam=exam
    ).exclude(status='in_progress').first()

    if completed_attempt:
        messages.warning(request, f"You have already completed '{exam.title}'. Only one attempt is permitted.")
        return redirect('exam_result_detail', attempt_id=completed_attempt.id)

    # Resume current or create new in-progress attempt
    attempt, created = ExamAttempt.objects.get_or_create(
        student=request.user,
        exam=exam,
        status='in_progress'
    )

    return redirect('take_exam', attempt_id=attempt.id)


@login_required
@student_required
def take_exam_view(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user,
        status='in_progress'
    )
    exam = attempt.exam
    questions = exam.questions.all()

    if request.method == 'POST':
        warning_count = int(request.POST.get('warning_count', 0))
        is_disqualified = request.POST.get('is_disqualified') == 'true'

        attempt.warning_count = warning_count
        attempt.is_disqualified = is_disqualified

        for question in questions:
            field_name = f"question_{question.id}"
            selected_option = request.POST.get(field_name)

            is_correct = (selected_option == question.correct_answer)
            marks_awarded = question.marks if is_correct else 0

            StudentAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'selected_option': selected_option,
                    'is_correct': is_correct,
                    'marks_obtained': marks_awarded
                }
            )

        attempt.submitted_at = timezone.now()
        attempt.calculate_final_score()

        if is_disqualified:
            messages.error(request, "Assessment auto-submitted: Exceeded maximum tab-switch / window violation limit.")
        else:
            messages.success(request, f"Exam '{exam.title}' submitted successfully!")
            
        return redirect('exam_result_detail', attempt_id=attempt.id)

    context = {
        'attempt': attempt,
        'exam': exam,
        'questions': questions,
        'duration_seconds': exam.duration_minutes * 60,
    }
    return render(request, 'results/take_exam.html', context)


@login_required
def exam_result_detail_view(request, attempt_id):
    if request.user.profile.is_student:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    else:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, exam__created_by=request.user)

    answers = attempt.answers.select_related('question').all()

    context = {
        'attempt': attempt,
        'exam': attempt.exam,
        'answers': answers,
    }
    return render(request, 'results/exam_result.html', context)


@login_required
def download_certificate_pdf_view(request, attempt_id):
    if request.user.profile.is_student:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    else:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, exam__created_by=request.user)

    if not attempt.passed or attempt.is_disqualified:
        messages.error(request, "Certificates are only issued for passing scores without security violations.")
        return redirect('exam_result_detail', attempt_id=attempt.id)

    template = get_template('results/certificate_pdf.html')
    context = {'attempt': attempt}
    html = template.render(context)
    
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"Certificate_{attempt.student.username}_{attempt.exam.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    messages.error(request, "Failed to render PDF certificate.")
    return redirect('exam_result_detail', attempt_id=attempt.id)


@login_required
def ai_diagnostic_analysis_view(request, attempt_id):
    if request.user.profile.is_student:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    else:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, exam__created_by=request.user)

    weak_answers = attempt.answers.filter(is_correct=False).select_related('question')
    weak_questions = [
        {
            'text': ans.question.question_text,
            'selected': ans.selected_option or 'Unanswered',
            'correct': ans.question.correct_answer,
        }
        for ans in weak_answers
    ]

    analysis = generate_student_diagnostic(
        exam_title=attempt.exam.title,
        total_marks=attempt.total_marks,
        earned_marks=attempt.score,
        percentage=float(attempt.percentage),
        weak_questions=weak_questions
    )

    return JsonResponse({'analysis': analysis})


@login_required
def doubt_chat_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            exam_context = data.get('context', 'General Examination')

            if not user_message:
                return JsonResponse({'reply': 'Please type a question.'})

            reply = get_doubt_bot_response(user_message, exam_context=exam_context)
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'reply': f"Error: {str(e)}"})

    return JsonResponse({'error': 'POST required'}, status=400)


@login_required
@student_required
def student_results_view(request):
    attempts = ExamAttempt.objects.filter(
        student=request.user
    ).exclude(status='in_progress').select_related('exam').order_by('-started_at')
    
    return render(request, 'results/student_results.html', {'attempts': attempts})