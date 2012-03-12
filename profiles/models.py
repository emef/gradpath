from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from degrees.models import Degree
     
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    courses = models.ManyToManyField(Course, blank=True)
    degrees = models.ManyToManyField(Degree, blank=True)

    def __unicode__(self):
        return 'Profile<%s>' % self.user.username
