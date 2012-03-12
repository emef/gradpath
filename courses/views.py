from django.http import HttpResponse
from courses.models import Section


def add_sections(request):
    for line in sections.splitlines():
        print line
        if ord(line[0]) != 65: 
            print line
            abbrv,name = line.split(' - ')
            s = Section(name=name, abbreviation=abbrv)
            s.save()

def add_from_csv(request):
    with open('/Users/mattforbes/school/492/scrape/demo.csv', 'r') as f:
        for line in f:
            section, number, title, description, credits = line.split(',')
            print section
            break
            
