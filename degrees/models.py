from django.conf import settings
from django.db import models
from courses.models import Course
from gradpath.degrees.evaluation.parser import parse_degree

class College(models.Model):
    name = models.CharField(max_length=150)

    def __unicode__(self):
        return 'College<%s>' % self.name

class Degree(models.Model):
    DEGREE_TYPES = (
        (1, 'Major'),
        (2, 'Minor'),
        (3, 'Certificate'),
    )
    name = models.CharField(max_length=150, unique=True)
    college = models.ForeignKey(College)
    degree_type = models.IntegerField(choices = DEGREE_TYPES)
    year = models.IntegerField()

    def xml(self):
        return '%s/%s.xml' % (settings.XML_PATH, self.name.replace(' ', '-').lower())
    
    def __unicode__(self):
        return 'Degree<%s>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'degree_type': self.degree_type,
            'year': self.year
        }

    def xml_to_json(self):
        evaluator = parse_degree(self)
        valid_attrs = ['node_type', 'mincredits', 'maxcredits', 'minsub', 
                       'id', 'section', 'minnumber', 'prereqs']
        
        def mk_node(req):
            node = {}
            for key in valid_attrs:
                if hasattr(req, key):
                    node[key] = getattr(req, key)
                    if isinstance(node[key], set):
                        node[key] = list(node[key])
                    
            if hasattr(req, 'subreqs'):
                node['children'] = [mk_node(subreq) for subreq in req.subreqs]
                
            #if hasattr(req, 'prereqs'):
            #    node['prereqs'] = [mk_node(prereq) for prereq in req.prereqs]
                
            return node

        from pprint import pprint
        val = mk_node(evaluator)
        pprint(val)
        return val
        #return mk_node(evaluator)
