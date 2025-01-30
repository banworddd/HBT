from django.shortcuts import redirect
from users.models import CustomUser

from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone

def check_user_status(request):
    if not request.user.is_authenticated:
        return redirect('startpage')

    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        return redirect('startpage')

    if not user.is_confirmed:
        return redirect('emailconfirmation')

    return None

def check_user_session(request, user_id):
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in active_sessions:
        session_store = SessionStore(session_key=session.session_key)
        session_data = session_store.load()
        if session_data.get('_auth_user_id') == str(user_id):
            return True
        else:
            pass

    return False
