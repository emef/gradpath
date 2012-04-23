from django.shortcuts import redirect
from gradpath import render_to, get_profile
from gradpath.courses.models import Course
from gradpath.profiles.models import Record

def create_degree(request):
    return render_to(request, 'administrator/create_degree.html', { 'key': 'val' })

def edit_degree(request):
    return render_to(request, 'administrator/edit_degree.html', { 'key': 'val' })

def create_admin(request):
    return render_to(request, 'administrator/create_admin.html', { 'key': 'val' })