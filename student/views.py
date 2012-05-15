from django.shortcuts import redirect
from django.http import HttpResponse
from gradpath import render_to, json_response
from gradpath.courses.models import Course, Section
from gradpath.degrees.models import Degree, College
from gradpath.profiles.models import Record, UserProfile
from gradpath.degrees.evaluation.parser import parse_degree
from decimal import Decimal
import re, datetime


######################################################################
# INFORMATION VIEWS

def progress(request):
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        progress = []
        records = dict([(r.course.id, r) for r in profile.records.all()])
        for degree in profile.degrees.all():
            evaluator = parse_degree(degree)
            evaluator.eval(records)
            print evaluator.creditcount, '/', evaluator.credit_worth()
            progress.append( {'degree': degree,
                              'evaluator': evaluator} )
        return render_to(request, 'student/progress.html', { 'progress': progress })
    else:
        # need to add a "please log in" message
        return render_to(request, 'student/student_base.html')

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
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        if profile:
            data = { 'records': profile.records.all()  }
        return render_to(request, 'student/courses/manage.html', data)
    else:
        # redirect to main
        return redirect('/student/')
        
#Helper function to remove course from the db
def courses_remove(request):
    profile = request.user.get_profile()
    course = Course.objects.get(id=int(request.GET['id']))
    Record.objects.filter(profile=profile, course=course).delete()
    return redirect('/student/courses/manage/')

# shows organized view of all courses, allows you to view/add them
def courses_list(request):
    return render_to(request, 'student/courses/list.html', {
        'sections': Section.objects.all()
    })
    
def courses_in_section(request, id):
    courses = Course.objects.filter(section=int(id))
    return json_response([c.to_json() for c in courses.all()])

def courses_add(request, id):
    if request.method == 'GET':
        return render_to(request, 'student/courses/getgradedate.html', {
                'course': Course.objects.get(id=int(id))
            })
    elif request.method == 'POST':
        grade = request.POST.get('grade', None)
        date = request.POST.get('date', None)
        date = datetime.date(int(request.POST.get('year')), 
                             int(request.POST.get('month')), 
                             int(request.POST.get('day')))
        profile = request.user.get_profile()
        course = Course.objects.get(id=id)
        
        try:
            Record.objects.get(profile=profile, course=course, grade=grade, date=date)
        except Record.DoesNotExist:
            Record.objects.create(profile=profile, course=course, grade=grade, date=date)
        except ValueError:
            pass

    return redirect('/student/courses/manage/')

######################################################################
# DEGREES VIEWS

def degrees_manage(request):
    if request.user.is_authenticated():
        user = request.user.get_profile()
        degrees = UserProfile.objects.get(id=user.id).degrees.all()
        degree_dict = {'degrees': degrees}
        return render_to(request, 'student/degrees/manage.html', degree_dict)
    else:
        # redirect to main
        return redirect('/student/')

def degrees_remove(request):
    user = request.user.get_profile()
    degree = Degree.objects.get(id=int(request.GET['id']))
    UserProfile.objects.get(id=user.id).degrees.remove(degree)
    return redirect('/student/degrees/manage/')

def degrees_list(request):
    return render_to(request, 'student/degrees/list.html', {
            'colleges': College.objects.all(),
    })

def degrees_in_college(request, id):
    degrees = Degree.objects.filter(college=int(id))
    return json_response([d.to_json() for d in degrees.all()])

def degrees_add(request, id):
    if request.user.is_authenticated():
        user = request.user.get_profile()
        degree = Degree.objects.get(id=id)
        UserProfile.objects.get(id=user.id).degrees.add(degree)
        return redirect('/student/degrees/manage/')
    else:
        return redirect('/student/')

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
                course = Course.objects.get(section__abbreviation=section,number=number)
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
