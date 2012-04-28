from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from gradpath.profiles.models import UserProfile

import simplejson as json

def render_to(request, template_name, *args):
    output = args[0] if len(args) > 0 else {}
    return render_to_response(template_name, output, context_instance=RequestContext(request))

def contains(obj, *args):
    return all (k in obj for k in args)
        

def extract(obj, *args):
    lst = []
    for key in args:
        lst.append(obj.get(key, None))
    return tuple(lst)


def json_response(resp):
    return HttpResponse(json.dumps(resp), mimetype="application/json")
