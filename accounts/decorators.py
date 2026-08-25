# FILE: accounts/decorators.py

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def teacher_required(view_func):
    """Restricts view access strictly to users with the Teacher role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Teacher privileges required.")
        return redirect('student_dashboard')
    return wrapper


def student_required(view_func):
    """Restricts view access strictly to users with the Student role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'profile') and request.user.profile.is_student:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Student portal only.")
        return redirect('teacher_dashboard')
    return wrapper