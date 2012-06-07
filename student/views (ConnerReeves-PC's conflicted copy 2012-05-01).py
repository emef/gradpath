from django.shortcuts import redirect
from gradpath import render_to, get_profile
from gradpath.courses.models import Course, Section
from gradpath.profiles.models import Record
from gradpath.degrees.evaluation import evaluate
from decimal import Decimal
import re, datetime


######################################################################
# INFORMATION VIEWS

def progress(request):
    profile = request.user.get_profile()
    progress = []
    for degree in profile.degrees.all():
        progress.append( {'degree': degree,
                          'passed': evaluate(request.user, degree) } )
    return render_to(request, 'student/progress.html', { 'progress': progress })

######################################################################
# COURSE VIEWS

GPA_MAP = {
    '4'   : 'A'  ,
    '3.7' : 'A-' ,
    '3.3' : 'B+' ,
    '3'   : 'B'  ,
    '2.7' : 'B-' ,
    '2.3' : 'C+' ,
    '2'   : 'C'  ,
    '1.7' : 'C-' ,
    '1.3' : 'D+' ,
    '1'   : 'D'  ,
    '0.7' : 'D-' ,
    '0'   : 'F'
}

# add/remove classes a student has selected
def courses_manage(request):
    profile = request.user.get_profile()
    if profile:
        records = profile.record_set.all()
	data = { 'records': profile.record_set.all()  }
	return render_to(request, 'student/courses/manage.html', data)
    else:
        # NOT IMPLEMENNTED
        pass
        
    return render_to(request, 'student/courses/manage.html')

#Helper function to remove course from the db
def courses_remove(request):
    profile = request.user.get_profile()
    course = Course.objects.get(id=int(request.GET['id']))
    Record.objects.filter(profile=profile, course=course).delete()
    return redirect('/student/courses/manage/')

def courses_remove_all(request):
    profile = request.user.get_profile()
    profile.records.all().delete()
    return redirect('/student/courses/manage/')

# shows organized view of all courses, allows you to view/add them
def courses_list(request):
    print "hello"
    print Course.objects.all()
    return render_to(request, 'student/courses/list.html', {
        'sections': Section.objects.all()
    })

######################################################################
# DEGREES VIEWS

def degrees_manage(request):
    return render_to(request, 'student/degrees/manage.html')

def degrees_list(request):
    return render_to(request, 'student/degrees/list.html')

######################################################################
# TRANSCRIPT VIEWS

TRANSCRIPT_RE = re.compile(r'([A-Z/]{2,4})[ ]+(\d{3})   (\d{5}) (.{1,31})\s*(\d)   ([A-FSU][-,+, ])   ([\d, ]\d.\d)   ([A-Z])  (\d\d)/(\d\d)/(\d\d)')

def transcript_import(request):
    user_input = request.POST.get('transcript', None)
        
    # POST REQUEST
    if user_input:
        courses = []
	dne = []
	multiple = []
	
	for match in re.finditer(TRANSCRIPT_RE, user_input):
            section, number = (str(match.group(1)), int(match.group(2)))
                        
	    try:
                course = Course.objects.get(section__abbreviation=section, 
                                                            number=number)
		grade = match.group(6)
		date = datetime.date(int(match.group(11)) + 2000, 
				     int(match.group(9)), 
				     int(match.group(10)))
		courses.append( (course, grade, str(date)) )
                                
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
            id = int(key.split(':')[0])
	    grade = key.split(':')[1]
	    dateTup = key.split(':')[2].split('-')
	    date = datetime.date(int(dateTup[0]), int(dateTup[1]), int(dateTup[2]))
	    course = Course.objects.get(id=id)
	    try:
                print str(course) + str(date)
		Record.objects.get(profile=profile, course=course, grade=grade, date=date)
	    except Record.DoesNotExist:
                Record.objects.create(profile=profile, course=course, grade=grade, date=date)
        except ValueError:
            pass
    return redirect('/student/courses/manage/')
