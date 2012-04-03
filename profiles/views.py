from django.shortcuts import render_to_response

def import_transcript(request):
    return render_to_response('user/import.html', {})

def register(request):
    return render_to_response('user/register.html', {})
