#!/usr/bin/env python
from django.core.management import setup_environ

import settings, sys, re
setup_environ(settings)
from courses.models import Course, Section
from degrees.models import College

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
    prereq_map = {}
    sec_map = {}
    
    def clean(string):
        return unicode(string.strip().replace('\n',''))
    def lookup_section(name):
        return Section.objects.get(abbreviation=name)
    def add_prereqs():
        patstr = '(?:%s) \d{3}' % '|'.join(s.abbreviation for s in Section.objects.all())
        pat = re.compile(patstr)
        for course_id, prereqs in prereq_map.items():
            course = Course.objects.get(pk=course_id)
            for cstr in pat.findall(prereqs):
                sec, num = cstr.strip().rsplit(' ', 1)
                if sec not in sec_map:
                    try:
                        sec_map[sec] = Section.objects.get(abbreviation=sec)
                    except:
                        print 'EXITING:', cstr
                        exit()
                try:
                    prereq = Course.objects.get(section=sec_map[sec], number=num)
                    course.prereqs.add(prereq)
                except:
                    print 'ERROR: ', sec, num
                    
    #remove old courses
    for course in Course.objects.all():
        #print 'course %s %s is being deleted' % (course.section.abbreviation, course.number)
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
                            credits = int(clean(credits)))
            course.save()

            prereq_map[course.id] = prereqs
            
    add_prereqs()
            
def populate_colleges():
    from data.college_list import COLLEGES

    #remove old colleges
    for college in College.objects.all():
        college.delete()
        
    for line in COLLEGES.splitlines():
        c = College(name=line)
        c.save()

IMPORT_FNS = {
    'sections': populate_sections,
    'courses': populate_courses,
    'colleges': populate_colleges
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
    
