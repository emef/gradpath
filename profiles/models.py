from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from courses.models import Course
from degrees.models import Degree
     
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    degrees = models.ManyToManyField(Degree, blank=True)

    def __unicode__(self):
        return 'Profile<%s>' % self.user.username

class Record(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='records')
    course = models.ForeignKey(Course)
    grade = models.CharField(max_length=3)
    date = models.DateField(auto_now=False, auto_now_add=False)
    
    def __unicode__(self):
        return 'Record<%s %s, %s>' % (self.course.section.abbreviation, 
                                      self.course.number, 
                                      self.grade)

    

# function called when User is created
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
# register signal
post_save.connect(create_user_profile, sender=User, dispatch_uid='create_user_profile')
        
