from django.shortcuts import redirect
from gradpath import render_to, get_profile
from gradpath.courses.models import Section, Course
from gradpath.settings import XML_PATH
import datetime,sys
from xml.etree.ElementTree import ElementTree

def open_degree(request):
    return render_to(request, 'administrator/open_degree.html', {
    	'years': range(2000, datetime.datetime.now().year + 5)
    })

def edit_degree(request):
	if request.method == 'POST':
		html = ''
		section = request.POST.get('section', None).lower()
		type = request.POST.get('type', None).lower()
		year = request.POST.get('year', None)
		filename = str(section + '_' + type + '_' + year + '.xml').replace(' ','_')
		if section and type and year:
			##Open the XML file
			try:
				xml_file = open(XML_PATH + '/' + filename, 'r')
			except:
				xml_file = open(XML_PATH + '/' + filename, 'w')
				xml_file.write('<xml>\n<degree section="' + section + '" type="' + type + '" year="' + year + '">\n</degree>\n</xml>')
				xml_file.close
				xml_file = open(XML_PATH + '/' + filename, 'r')
				
			#Convert to ElementTree object
			xml_tree = ElementTree()
			xml_tree.parse(xml_file)

			groups = xml_tree.findall('degree/group')
			for group in groups:
				html += '<div class="req">'
			   #List the min number of sub reqs				
				try:
					html += 'Minimum: ' + group.attrib['min']
				except:
					html += 'All Required'
				#Output match elements
				matches = group.findall('match')
				for match in matches:
					try:
						#If an id is given than only one class will matches			
						course = Course.objects.get(id=match.attrib['id'])
						html += '<div>' + course.section.abbreviation + ' ' + str(course.number) + '</div>'
					except:
						sec = match.attrib.get('section', None)
						num = match.attrib.get('number', None)
						cre =	match.attrib.get('credits', None)
						html += '<div>'
						if cre:
							if cre[0] == '>':
								html += 'At least ' + str(int(cre.lstrip('>')) + 1) + ' credits from '
						if sec:
							html += Section.objects.get(id=sec).name
						if num:
							if num[0] == '>':
								html += ' (' + str(int(num.lstrip('>')) + 1) + ' level or above)'
						html += '</div>'

				html += '</div>'	#End Group	
		
			print html
			#match_elements = xml_tree.findall('.//match')
			#for match in match_elements:
			#	try:
			#		#If an id is given than only one class will matches			
			#		course = Course.objects.get(id=match.attrib['id'])
			#
			#	except:
			#		pass			
			
			return render_to(request, 'administrator/edit_degree.html', {
				'section': section.title(),
				'type': type.title(),
				'year': year,
				'html': html
			})
	return redirect('/administrator/open_degree/')

def create_admin(request):
    return render_to(request, 'administrator/create_admin.html', { 'key': 'val' })