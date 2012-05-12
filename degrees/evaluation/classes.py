from gradpath.courses.models import Course, Section

NODE_DEGREE = 'degree'
NODE_GROUP = 'group'
NODE_MATCH = 'match'
NODE_EXCEPT = 'except'
NODE_REPEATABLE = 'repeatable'
NODE_PREREQS = 'prereqs'
    
class Req(object):
    def __init__(self, attrs, node_type):
        self.node_type = node_type
        self.reset()
        
        for key,val in attrs.items():
            try:
                val = int(val)
            except ValueError:
                pass
            self.__dict__[key] = val
        
    def __str__(self):
        return '<%s />' % self.node_type

    def reset(self):
        self.passed = False
        self.creditcount = 0
        self.coursecount = 0
        self.consumed = set()


def get_int_or_none(obj, key):
    return int(obj[key]) if key in obj else None

class Container(Req):
    def __init__(self, attrs, node_type):
        super(Container, self).__init__(attrs, node_type)
        self.ignore = []
        self.subcount = 0
        self.minsubcount = get_int_or_none(self.__dict__, 'minsub')
        self.mincreditcount = get_int_or_none(self.__dict__, 'mincredits')
        self.maxcreditcount = get_int_or_none(self.__dict__, 'maxcredits')

        self._subreqs = []
        self._courses = []
        self._matches = []
        self._containers = []
    
    @property
    def subreqs(self):
        return self._subreqs
        #return self._courses + self._matches + self._containers

    def add(self, node):
        self._subreqs.append(node)
        #if isinstance(node, Match):
        #    if node.is_course:
        #        self._courses.append(node)
        #    else:
        #        self._matches.append(node)
        #else:
        #    self._containers.append(node)
            
    def pprint(self, spaces=''):
        print spaces, '<', self.node_type, '>'
        for r in self.subreqs: r.pprint(spaces + '  ')

    def doc(self, text=None):
        return {
            'text': text,
            'children': [sub.doc() for sub in self.subreqs if not sub.passed]
        }
        

class Degree(Container):
    def __init__(self, attrs):
        super(Degree, self).__init__(attrs, NODE_DEGREE)
        
    def doc(self, text=None):
        text = text if text else 'Degree requires:'
        return super(Degree, self).doc(text)
        
    def eval(self, records, ignore=None):
        if ignore == None:
            ignore = {}
        count = 0
        for sub in self.subreqs:
            sub.eval(records, [])
            count += 1 if sub.passed else 0
            self.creditcount += sub.creditcount
            self.coursecount += sub.coursecount
        self.passed = count == len(self.subreqs)
        
class Group(Container):
    def __init__(self, attrs):
        super(Group, self).__init__(attrs, NODE_GROUP)

    def doc(self):
        sub_clause = None
        credit_clause = None
        
        if (self.minsubcount is not None) and self.subcount < self.minsubcount:
            sub_clause = self.minsubcount - self.subcount
        if (self.mincreditcount is not None) and self.creditcount < self.mincreditcount:
            credit_clause = '{0} credits'.format(self.mincreditcount - self.creditcount)
            
        if sub_clause and credit_clause:
            text = '{0} of the following with {1} credits:'.format(sub_clause, credit_clause)
        elif sub_clause:
            text = '{0} of the following:'.format(sub_clause)
        elif credit_clause:
            text = '{0} credits from:'.format(credit_clause)
        else:
            text = 'All of:'
            
        return super(Group, self).doc(text)
        
    def eval(self, records, ignore):
        # join the ignore lists
        joined_ignore = ignore + self.ignore

        # make a copy of the records
        records = records.copy()
        
        # evaluate the subreqs recursively
        for sub in self.subreqs:
            sub.eval(records, joined_ignore)
            self.creditcount += sub.creditcount
            self.coursecount += sub.coursecount

            # join consumed sets
            for id in sub.consumed:
                self.consumed.add(id)
                del records[id]
                
            if sub.passed:
                self.subcount += 1
                
        
        # record credits for after-evaluation analysis
        # credits_earned <= mincredits if mincredits exists
        if self.mincreditcount > 0 and self.creditcount > self.mincreditcount:
            self.creditcount = self.mincreditcount

        # set passed flag
        self.passed = True
        if self.minsubcount is not None:
            if self.subcount < self.minsubcount:
                self.passed = False
        elif self.subcount < len(self.subreqs):
            try:
                print self.name, self.subcount, len(self.subreqs)
            except: pass
            self.passed = False
            
        if (self.mincreditcount is not None) and self.creditcount < self.mincreditcount:
            self.passed = False

    def __str__(self):
        name = getattr(self, 'name', '')
        return '<group {0} />'.format(name)
        
        
class Repeatable(Container):
    def __init__(self, attrs):
        super(Repeatable, self).__init__(attrs, NODE_REPEATABLE)
        self.passed = False

    def doc(self):
        text = 'Up to {0} credits of:' if self.maxcreditcount else 'Any of:'
        return super(Repeatable, self).doc(text)
        
    def eval(self, records, ignore):
        # copy records so we can modify
        records = records.copy()

        # join the ignore lists
        joined_ignore = ignore + self.ignore
        
        for sub in self.subreqs:
            valid = True
            while valid:
                sub.eval(records, joined_ignore)

                self.creditcount += sub.creditcount
                self.coursecount += sub.coursecount

                if self.maxcreditcount and self.creditcount > self.maxcreditcount:
                    self.creditcount = self.maxcreditcount
                
                for id in sub.consumed:
                    self.consumed.add(id)
                    del records[id]
                
                valid = sub.passed
                if self.maxcreditcount:
                    valid = valid and self.creditcount < self.maxcreditcount
                sub.reset()
        

class Match(Req):
    def __init__(self, attrs):
        super(Match, self).__init__(attrs, NODE_MATCH)
        self.prereqs = set()

    def __str__(self):
        valid = ['id', 'section', 'number', 'credits']
        keys = (key for key in self.__dict__ if key in valid)
        attrs = ' '.join('{0}={1}'.format(key, self.__dict__[key]) for key in keys)
        return '<match {0} />'.format(attrs)
        
    def pprint(self, spaces=''):
        print '%s<match>' % spaces

    def doc(self):
        if hasattr(self, 'id'):
            return {'text': Course.shortcut(self.id).full_str(), 'children': None}
        else:
            text = 'Any courses '
            if hasattr(self, 'section'):
                text += 'from section {0} '.format(Section.shortcut(self.section).name)
            if hasattr(self, 'number'):
                text += 'with course number {0}'.format(self.number)
            text += ':'
            
            prereq_doc = None
            if len(self.prereqs):
                children = []
                for cstr in (Course.shortcut(id).full_str() for id in self.prereqs):
                    children.append({'text': cstr, 'children': None})
                prereq_doc = [{'text': 'With pre-requisites:',
                              'children': children}]
                    
            return {'text': text, 'children': prereq_doc }
                    
        
    @property
    def is_course(self):
        return hasattr(self, 'id')

    def test(self, r):
        # test for simple course
        if self.is_course:
            return r.course.id == self.id

        # test section ID
        if hasattr(self, 'section'):
            if r.course.section.id != self.section:
                return False
                    
        # test course number
        if hasattr(self, 'number'):
            if self.number[0] == '>':
                min_num = int(self.number[1:])
                if r.course.number <= min_num:
                    return False
            else:
                raise NameError('NOT IMPLEMENTED')

        # test credits
        if hasattr(self, 'credits'):
            if self.credits[0] == '>':
                min_credits = int(self.credits[1:])
                if r.course.credits <= min_credits:
                    return False
            else:
                raise NameError('NOT IMPLEMENTED')

        # check prereqs: course must have ONE of these prereqs
        if len(self.prereqs) > 0:
            for id in self.prereqs:
                found = False
                if r.course.has_prereq(id):
                    found = True
                    break
            if not found:
                return False
            
        # passed all tests
        return True
    
    def eval(self, records, ignore):
        for id,r in records.items():
            # ignore any records that are in the ignore list
            if any( ignored.test(r) for ignored in ignore ):
                # ignore this record
                continue
            
            if self.test(r):
                self.creditcount = r.course.credits
                self.passed = True
                self.consumed.add(id)
                return
                
        # dropped through, did not find a match
        self.passed = False

        
classmap = {
    NODE_DEGREE: Degree,
    NODE_GROUP: Group,
    NODE_REPEATABLE: Repeatable,
    NODE_MATCH: Match,
}
    
def make_req(node_type, attrs):
    return classmap[node_type](attrs)
