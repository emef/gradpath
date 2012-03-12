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
    name = models.CharField(max_length=150)
    college = models.ForeignKey(College)
    degree_type = models.IntegerField(choices = DEGREE_TYPES)

    def __unicode__(self):
        return 'Degree<%s>' % self.name
