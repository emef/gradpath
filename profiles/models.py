from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from degrees.models import Degree
     
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    degrees = models.ManyToManyField(Degree, blank=True)

    def __unicode__(self):
        return 'Profile<%s>' % self.user.username

class Record(models.Model):
    course = models.ForeignKey(Course)
    grade = models.DecimalField(blank=True, max_digits=3, decimal_places=2)
    
    def __unicode__(self):
        return 'Record<%s %s, %s>' % (self.course.section.abbreviation, 
                                      self.course.number, 
                                      self.grade)

    
