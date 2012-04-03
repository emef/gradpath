from django.shortcuts import render_to_response
from courses.models import Section

def preview(request,id):
	return render_to_response('preview.html', {})