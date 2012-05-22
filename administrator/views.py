from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import redirect
from gradpath import render_to, contains, extract, json_response
from gradpath.courses.models import Section, Course
from gradpath.degrees.models import College, Degree
from datetime import datetime

###########################################################################
# page views

def new_degree(request):
    if request.method == 'POST':
        args = ['name', 'degree_type', 'college_id', 'year']
        
        if not contains(request.POST, *args):
            print request.POST
            print 'MISSING KEY IN POST DICT'
            raise Http404
        
        name, degree_type, college_id, year = extract(request.POST, *args)
        
        # ensure it doesn't exist
        try:
            degree = Degree.objects.get(name=name, 
                                        college__id=college_id, 
                                        degree_type=degree_type,
                                        year=year)
                                        
        except Degree.DoesNotExist:
            # we need to create it
            degree = Degree(name=name, degree_type=degree_type, year=year)
            degree.college_id = college_id
            degree.save()
            # create xml file
            open(degree.xml(), "w")
            
        # go edit the degree
        return redirect('administrator.views.edit_degree', id=degree.id)
                        
    # GET request:
    colleges = College.objects.all()
    return render_to(request, 'administrator/new_degree.html', {
            'colleges': colleges,
            'degree_types': Degree.DEGREE_TYPES,
            'years': range(2000, datetime.now().year + 3),
    })

def open_degree(request):
    degrees = Degree.objects.all()
    return render_to(request, 'administrator/open_degree.html', {
            'degrees': degrees,
    })

def edit_degree(request, id):
    try:
        degree = Degree.objects.get(pk=id)
    except Degree.DoesNotExist:
        print 'DEGREE DOES NOT EXIST'
        raise Http404
        
    return render_to(request, 'administrator/edit_degree.html', {
        'degree': degree,
    })

def create_admin(request):
    output = {}
    if request.user.is_authenticated() and request.user.is_superuser:
        if request.method == 'POST':
            errors = {}
        
            # extract values from POST, will be None if not present
            username, pw1, pw2 = extract(request.POST, 'username', 'password1', 'password2')
        
            # begin validation...
            if username is None or len(username) == 0:
                errors['username'] = 'Required'
            else:
                try:
                    user = User.objects.get(username=username)
                    #user.delete()
                    errors['username'] = 'That universal login was already registered.'
                except User.DoesNotExist:
                    # good
                    pass

            if pw1 is None or len(pw1) == 0:
                errors['password1'] = 'Required'

            if pw2 is None  or len(pw2) == 0:
                errors['password2'] = 'Required'

            if pw1 != pw2:
                errors['password1'] = 'Passwords must match'

            # ... end of validation
            
            if len(errors) == 0:
                user = User(username=username)
                user.set_password(pw1)
                user.is_active = True
                user.is_superuser = True
                user.is_staff = True
                user.save()
                
                return render_to(request, 'administrator/register_success.html', {
                	'username':username
                })
                
            output['errors'] = errors
            output['username'] = username
                
        # fall through if errors
        return render_to(request, 'administrator/register.html', output)


###########################################################################
# AJAX API

def save_degree(request):
    pass


def ajax_sections(request):
    return json_response([section.to_json() for section in Section.objects.all()])
      
