import xml.parsers.expat
from gradpath.degrees.evaluation.classes import *


CONTAINERS = set([NODE_DEGREE,
                  NODE_GROUP,
                  NODE_MATCH,
                  NODE_REPEATABLE, 
])


# Parse_degree:
# RETURNS:  degree object 
# (user):   User object (django.auth)
# (degree): Degree object (gradpath.degrees)
def parse_degree(degree):
    # parent has to be a list (hack)
    stack = []
    parent = [None]
    isexcept = [False]
    isprereqs = [False]
    
    # parser functions
    def start_element(name, attrs):
        # special cases
        if name == NODE_EXCEPT:
            isexcept[0] = True
        elif name == NODE_PREREQS:
            isprereqs[0] = True
        elif name == NODE_DEGREE:
            node = make_req(name, attrs)
        elif name == 'xml':
            pass
        else:
            node = make_req(name, attrs)
            if isexcept[0]:
                parent[0].ignore.append(node)
            elif isprereqs[0]:
                try:
                    parent[0].prereqs.add(node.id)
                except:
                    print 'ERROR parsing! prereq should ONLY be a <match id=X />'
            else:
                parent[0].add(node)
                
                
        if name in CONTAINERS:
            stack.append(node)
            parent[0] = node
            
    def end_element(name):
        # close <group> nodes
        if name in CONTAINERS:
            stack.pop()
            if len(stack) > 0:
                parent[0] = stack[-1]
        elif name == NODE_EXCEPT:
            isexcept[0] = False
        elif name == NODE_PREREQS:
            isprereqs[0] = False
        
    # Create the parser
    p = xml.parsers.expat.ParserCreate()

    # assign the handlers
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    
    # parse the degree's xml file
    with open(degree.xml(), 'r') as f:
        p.ParseFile(f)

    parent = parent[0]
    
    # sanity check
    if parent.node_type != NODE_DEGREE:
        raise NameError('Invalid parse')

    return parent
    
