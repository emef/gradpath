from django.template import RequestContext
from django.shortcuts import render_to_response
from gradpath.profiles.models import UserProfile

def render_to(request, template_name, *args):
    output = args[0] if len(args) > 0 else {}
    return render_to_response(template_name, output, context_instance=RequestContext(request))

def extract(obj, *args):
    lst = []
    for key in args:
        lst.append(obj.get(key, None))
    return tuple(lst)

def get_profile(request):
    try:
        return UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return None
    
