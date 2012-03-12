#!/usr/bin/env python
from django.core.management import setup_environ

import settings, sys
setup_environ(settings)
from courses.models import Course, Section

def populate_sections():
    from data.section_list import SECTIONS

    #remove old sections
    for section in Section.objects.all():
        section.delete()
        
    for line in SECTIONS.splitlines():
        abbrv,name = line.split(' - ')
        s = Section(name=name, abbreviation=abbrv)
        s.save()

def populate_courses():
    def clean(string):
        return string.strip().replace('\n','').replace(r"[\x90-\xff]", '')
    def lookup_section(name):
        return Section.objects.get(abbreviation=name)
    
    #remove old courses
    for course in Course.objects.all():
        print 'course %s %s is being deleted' % (course.section.abbreviation, course.number)
        course.delete()
    
    with open('data/courses.csv', 'r') as f:
        for line in f:
            line = line.replace('", "', '|').replace('"', '').replace('\n', '')
            section_name, number, title, descr, prereqs, credits = line.split('|')
            
            section = lookup_section(clean(section_name))
            if section is None:
                print 'Unknown section: %s' % section_name
                exit()
            
            course = Course(title = clean(title),
                            section = section,
                            number = int(clean(number)),
                            description = descr,
                            prereqs = clean(prereqs),
                            credits = int(clean(credits)))
                            
            course.save()
                            

IMPORT_FNS = {
    'sections': populate_sections,
    'courses': populate_courses,
}

if __name__ == '__main__':
    def usage():
        print 'Usage: %s %s' % (sys.argv[0], ' | '.join(IMPORT_FNS.keys()))
        
    if len(sys.argv) < 2:
        usage()
        exit()
        
    fn = IMPORT_FNS.get(sys.argv[1], None)
    if fn is not None:
        fn()
    else:
        usage()
    
