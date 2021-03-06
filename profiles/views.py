from django.shortcuts import render_to_response, redirect
from gradpath import render_to, extract, json_response
from gradpath.profiles.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
REQUIRE_ACTIVATION = settings.REQUIRE_ACTIVATION

def home(request):
    return render_to(request, 'profiles/home.html')

def import_transcript(request):
    return render_to(request, 'profiles/import.html')
    
def logout_user(request):
    logout(request)
    return redirect('/')

# AJAX REQUEST
@csrf_exempt
def login_user(request):
    username, password = extract(request.POST, 'username', 'password')
    user = authenticate(username=username, password=password)
    error = None
    if user is not None:
        if settings.REQUIRE_ACTIVATION and not user.active:
            # user created, but didn't finish email activation
            error = 'This account has not been activated, please see your email or click <here>.'
        else:
            # success
            login(request, user)
    else:
        error = 'Username/password combination was incorrect.'
        
    resp = None
    if error is not None:
        resp = {'status': 'error',
                'message': error}
    else:
        # CHANGE REDIRECT BASED ON USER'S GROUP
        resp = {'status': 'okay',
                'redirect': '/student/courses/manage/'}
        
    return json_response(resp)


def get_courses(request, section_id):
    courses = Course.objects.filter(section__id=section_id);
    return json_response([c.to_json() for c in courses])


def register_user(request):
    output = {}
    if request.method == 'POST':
        errors = {}
        
        # extract values from POST, will be None if not present
        username, pw1, pw2 = extract(request.POST, 'username', 'password1', 'password2')
        
        # begin validation...
        if username is None  or len(username) == 0:
            errors['username'] = 'Required'
        else:
            try:
                user = User.objects.get(username=username)
                #user.delete()
                errors['username'] = 'That universal login was already registered.'
            except User.DoesNotExist:
                # good
                pass

        if pw1 is None or len(pw1) == 0:
            errors['password1'] = 'Required'

        if pw2 is None  or len(pw2) == 0:
            errors['password2'] = 'Required'

        if pw1 != pw2:
            errors['password1'] = 'Passwords must match'

        # ... end of validation
        
        if len(errors) == 0:
            user = User(username=username)
            user.set_password(pw1)
            user.is_active = True
            user.save()
            
            # SUCCESS, redirect...
            if REQUIRE_ACTIVATION:
                # set active flag to false until email verified
                user.is_active = False
                user.save()
                return redirect('/activate')
            else:
                # don't need to verify. log user in and go to home 
                user.backend='django.contrib.auth.backends.ModelBackend' 
                login(request, user)
                return redirect('/')
            
        output['errors'] = errors
        output['username'] = username
            
    # fall through if errors
    return render_to(request, 'profiles/register.html', output)

def activate(request):
    pass
    
def home(request):
  return redirect('/student/')
