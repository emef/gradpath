from django.shortcuts import render_to_response, redirect
from gradpath import render_to, extract
from gradpath.profiles.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings
REQUIRE_ACTIVATION = settings.REQUIRE_ACTIVATION

def register(request):
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
            # first create User, then UserProfile
            user = User(username=username)
            user.set_password(pw1)
            user.is_active = True
            user.save()

            profile = UserProfile(user=user)
            profile.save()
            
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
