from gradpath.courses.models import Course

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

class Container(Req):
    def __init__(self, attrs, node_type):
        super(Container, self).__init__(attrs, node_type)
        self.subreqs = []
        self.ignore = []
        self.subcount = 0

    def add(self, node):
        if isinstance(node, Match) and node.is_course:
            self.subreqs.insert(0, node)
        else:
            self.subreqs.append(node)

    def pprint(self, spaces=''):
        print spaces, '<', self.node_type, '>'
        for r in self.subreqs: r.pprint(spaces + '  ')

class Degree(Container):
    def __init__(self, attrs):
        super(Degree, self).__init__(attrs, NODE_DEGREE)
        
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
                
        minsubcount = int(getattr(self, 'min', len(self.subreqs)))
        mincreditcount = int(getattr(self, 'credits', 0))
        
        # record credits for after-evaluation analysis
        # credits_earned <= mincredits if mincredits exists
        if mincreditcount > 0 and self.creditcount > mincreditcount:
            self.creditcount = mincreditcount

        # set passed flag
        self.passed = self.subcount >= minsubcount and \
                      self.creditcount >= mincreditcount
        
        
class Repeatable(Container):
    def __init__(self, attrs):
        super(Repeatable, self).__init__(attrs, NODE_REPEATABLE)
        self.passed = True

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

                for id in sub.consumed:
                    self.consumed.add(id)
                    del records[id]
                
                valid = sub.passed
                sub.reset()
        

class Match(Req):
    def __init__(self, attrs):
        super(Match, self).__init__(attrs, NODE_MATCH)
        self.prereqs = set()

    def pprint(self, spaces=''):
        print '%s<match>' % spaces
        
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
