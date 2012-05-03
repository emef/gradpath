from django.db import models

class Section(models.Model):
    name = models.CharField(max_length=150)
    abbreviation = models.CharField(max_length=4)

    def __unicode__(self):
        return 'Section<%s>' % self.name

    def to_json(self):
        return {
            'name': self.name,
            'abbreviation': self.abbreviation
        }

class Course(models.Model):
    title = models.CharField(max_length = 200)
    section = models.ForeignKey(Section)
    number = models.IntegerField()
    description = models.TextField()
    prereqs = models.ManyToManyField("self", symmetrical=False)
    credits = models.IntegerField()
    notes = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return 'Course<%s %d>' % (self.section.abbreviation, self.number)

    @staticmethod
    def shortcut(*args):
        if type(args[0]) is int:
            return Course.objects.get(pk=args[0])
        elif len(args) == 2:
            return Course.objects.get(section__abbreviation=args[0], number=args[1])
    
    def prereq_chain(self):
        def populate_chain(chain, pr):
            if not pr.id in chain:
                chain.add(pr.id)
                for subpr in pr.prereqs.all():
                    populate_chain(chain, subpr)
            
        
        if not hasattr(self, '_prereq_chain'):
            self._prereq_chain = set()
            for pr in self.prereqs.all():
                populate_chain(self._prereq_chain, pr)
        
        return self._prereq_chain
        
    def has_prereq(self, course_id):
        return course_id in self.prereq_chain()

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'section': self.section.to_json(),
            'number': self.number,
            'description': self.description,
#            'prereqs': [pr.to_json() for pr in self.prereqs.all()],
            'credits': self.credits,
            'notes': self.notes
        }
                
