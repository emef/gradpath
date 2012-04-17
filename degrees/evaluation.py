import xml.parsers.expat

# node types
NODE_DEGREE = 'degree'
NODE_GROUP = 'group'
NODE_COURSE = 'course'
NODE_MATCH = 'match'
NODE_EXCEPT = 'except'

# class req
# used to build a recursive evaluator of a given degree xml
# built during the parse of the xml
class req():
    def __init__(self, node_type, attrs):
        self.node_type = node_type
        self.subreqs = []
        self.ignore = []
        
        for key,val in attrs.items():
            try:
                val = int(val)
            except ValueError:
                pass
            self.__dict__[key] = val
        
    def __str__(self):
        for key,val in self.__dict__.items():
            print key,'=',val
        return self.node_type
    
    def output(self, spaces=''):
        print spaces, '<', self.node_type, '>'
        for r in self. subreqs: r.output(spaces + '  ')
            
    def match(self, r):
        # test course ID
        if hasattr(self, 'id'):
            if r.course.id != self.id:
                return False
        
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
        
        # passed all tests
        return True
            
    # evaluate this requirement
    # RETURNS:   True or False
    # (records): dict of { id: Record } for quick id lookups
    # (ignore):  dict of { id: req } that will be ignored 
    def eval(self, records, ignore):
        # <DEGREE>
        if self.node_type == NODE_DEGREE:
            return all(sub.eval(records, []) for sub in self.subreqs)
        
        # <GROUP>
        elif self.node_type == NODE_GROUP:
            # evaluate sub requirements recursively
            joint_ignore = ignore + self.ignore
            sub_eval = [sub.eval(records, joint_ignore) for sub in self.subreqs]

            # count number of satisfied sub requirements
            satisfied = sum( x == True for x in sub_eval)

            # return true if satisfied >= min
            minimum = int(getattr(self, 'min', len(self.subreqs)))
            return satisfied >= minimum
                
        # <MATCH>
        elif self.node_type == NODE_MATCH:
            for r in records.values():
                # ignore any records that are in the ignore list
                if any( ignore_req.match(r) for ignore_req in ignore ):
                    # ignore this record
                    continue
                
                if self.match(r):
                    return True
                
            # dropped through, did not find a match
            return False
                
        # unknown node type
        else:
            raise NameError('Invalid node type: <%s>'% self.node_type)

# evaluate:
# RETURNS:  True or False (if user has completed degree)
# (user):   User object (django.auth)
# (degree): Degree object (gradpath.degrees)
def evaluate(user, degree):
    # parent has to be a list (hack)
    stack = []
    parent = [None]
    isexcept = [False]
    
    # parser functions
    def start_element(name, attrs):
        node = req(name, attrs)
        
        # cases
        if name == NODE_DEGREE:
            stack.append(node)
            parent[0] = node
        elif name == NODE_EXCEPT:
            isexcept[0] = True
        elif name == NODE_GROUP:
            parent[0].subreqs.append(node)
            parent[0] = node
            stack.append(parent[0])
        elif name == NODE_MATCH or name == NODE_COURSE:
            if not isexcept[0]:
                parent[0].subreqs.append(node)
            else:
                parent[0].ignore.append(node)
        elif name == 'xml':
            pass
        else:
            raise NameError('Invalid node type: <%s>' % name)
            
    def end_element(name):
        # close <group> nodes
        if name == NODE_GROUP:
            stack.pop()
            parent[0] = stack[-1]
        elif name == NODE_EXCEPT:
            isexcept[0] = False
        
    # Create the parser
    p = xml.parsers.expat.ParserCreate()

    # assign the handlers
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    
    # parse the degree's xml file
    with open(degree.xml(), 'r') as f:
        p.ParseFile(f)

    parent = parent[0]
    parent.output()
        
    # sanity check
    if parent.node_type != NODE_DEGREE:
        raise NameError('Invalid parse')

    # records object, a dictionary with form: { courseID: Record }
    records = dict([(r.course.id, r) for r in user.get_profile().record_set.all()])
        
    # perform the recursive evaluation!
    return parent.eval(records, {})
    
