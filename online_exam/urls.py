# FILE: online_exam/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)

def custom_permission_denied(request, exception):
    return render(request, '403.html', status=403)

def custom_server_error(request):
    return render(request, '500.html', status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('exams/', include('exams.urls')),
    path('results/', include('results.urls')),
]

handler404 = custom_page_not_found
handler403 = custom_permission_denied
handler500 = custom_server_error