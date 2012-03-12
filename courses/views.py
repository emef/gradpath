from django.http import HttpResponse
from django.shortcuts import render_to_response
from courses.models import Section

def home(request):
    return render_to_response('home.html', {})
