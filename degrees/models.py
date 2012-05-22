from django.conf import settings
from django.db import models
from courses.models import Course

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
        return '%s/%s-%s.xml' % (settings.XML_PATH, self.name.replace(' ', '-').lower(), self.year)
    
    def __unicode__(self):
        return 'Degree<%s>' % self.name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'degree_type': self.degree_type,
            'year': self.year
        }
