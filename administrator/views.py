from django.shortcuts import redirect
from gradpath import render_to, get_profile
from gradpath.courses.models import Section
from gradpath.settings import XML_PATH
import datetime,sys

def open_degree(request):
    return render_to(request, 'administrator/open_degree.html', {
    	'years': range(2000, datetime.datetime.now().year + 5)
    })

def edit_degree(request):
	if request.method == 'POST':
		section = request.POST.get('section', None).lower()
		type = request.POST.get('type', None).lower()
		year = request.POST.get('year', None)
		filename = str(section + '_' + type + '_' + year + '.xml').replace(' ','_')
		print filename
		if section and type and year:
			##Open the XML file
			try:
				xml_file = open(XML_PATH + '/' + filename, 'r')
			except:
				xml_file = open(XML_PATH + '/' + filename, 'w')

				xml_file.write('<xml>\n<degree section="' + section + '" type="' + type + '" year="' + year + '">\n</degree>\n</xml>')

			##Render the results

			return render_to(request, 'administrator/edit_degree.html', {
				'section': section.title(),
				'type': type.title(),
				'year': year
			})
	return redirect('/administrator/open_degree/')

def create_admin(request):
    return render_to(request, 'administrator/create_admin.html', { 'key': 'val' })