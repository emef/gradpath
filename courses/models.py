from django.db import models

class Section(models.Model):
    name = models.CharField(max_length=150)
    abbreviation = models.CharField(max_length=4)

    def __unicode__(self):
        return 'Section<%s>' % self.name

class Course(models.Model):
    title = models.CharField(max_length = 200)
    section = models.ForeignKey(Section)
    number = models.IntegerField()
    description = models.TextField()
    prereqs = models.CharField(max_length = 400)
    credits = models.IntegerField()
    notes = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return 'Course<%s %d>' % (self.section.abbreviation, self.number)
