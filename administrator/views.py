from django.http import Http404
from django.shortcuts import redirect
from gradpath import render_to, contains, extract
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
    return render_to(request, 'administrator/create_admin.html', { 'key': 'val' })


###########################################################################
# AJAX API

def save_degree(request):
    pass
