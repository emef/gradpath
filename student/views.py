from django.shortcuts import redirect
from gradpath import render_to, get_profile
from gradpath.courses.models import Course
from gradpath.profiles.models import Record
import re

######################################################################
# INFORMATION VIEWS

def progress(request):
    return render_to(request, 'student/progress.html')

######################################################################
# COURSE VIEWS

# add/remove classes a student has selected
def courses_manage(request):
    profile = request.user.get_profile()
    if profile:
        data = { 'records': [(r.course, r.grade) for r in profile.record_set.all()]  }
        return render_to(request, 'student/courses/manage.html', data)
    else:
        # NOT IMPLEMENNTED
        pass
    
    return render_to(request, 'student/courses/manage.html')

# shows organized view of all courses, allows you to view/add them
def courses_list(request):
    return render_to(request, 'student/courses/list.html')

######################################################################
# DEGREES VIEWS

def degrees_manage(request):
    return render_to(request, 'student/degrees/manage.html')

def degrees_list(request):
    return render_to(request, 'student/degrees/list.html')

######################################################################
# TRANSCRIPT VIEWS
TRANSCRIPT_RE = re.compile(r'([A-Z/]{2,4})[ ]+(\d{3})')
    
def transcript_import(request):
    user_input = request.POST.get('transcript', None)
    
    # POST REQUEST
    if user_input is not None:
        courses = []
        dne = []
        multiple = []
        
        for match in re.finditer(TRANSCRIPT_RE, user_input):
            section, number = (str(match.group(1)), int(match.group(2)))
            
            try:
                course = Course.objects.get(section__abbreviation=section, 
                                            number=number)
                courses.append(course)
                
            except Course.DoesNotExist:
                dne.append( (section, number) )
            
            except Course.MultipleObjectsReturned:
                # email administrators about the error
                # don't add any, but tell the student something broke
                multiple.append( (section, number) )
            
        data = { 'courses': courses,
                 'dne': dne,
                 'multiple': multiple }
        
        return render_to(request, 'student/transcript/verify.html', data)
                         

    # GET REQUEST
    else:
        return render_to(request, 'student/transcript/import.html')
            
        
def transcript_submit(request):
    # if everything okay
    profile = request.user.get_profile()
    
    for key,val in request.POST.items():
        try:
            id = int(key)
            course = Course.objects.get(id=id)
            Record.objects.create(profile=profile, course=course, grade='4.0')
        except ValueError:
            pass
    return redirect('/student/courses/manage/')
