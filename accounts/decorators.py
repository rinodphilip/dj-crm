from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view(request,*args,**kwargs)
    return wrapper

def allowed_users(allowed_roles=[]):
    def dec(view):
        def wrapper(request,*args,**kwargs):
            groups = None
            if request.user.groups.exists():
                groups = [g.name for g in request.user.groups.all()]
                if set(groups).intersection(allowed_roles):
                    return view(request,*args,**kwargs)
                else:
                    return HttpResponse("Please login with a customer profile")              
        return wrapper
    return dec

def admin_only(view):
    def wrapper(request,*args,**kwargs):
        groups = None
        if request.user.groups.exists():
            groups = [g.name for g in request.user.groups.all()]
            if 'admin' in groups:
                return view(request,*args,**kwargs)
            if 'customer' in groups:
                return redirect('user_page')
    return wrapper