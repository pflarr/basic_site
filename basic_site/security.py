import datetime

from models import DBSession, User
from pyramid.security import remember
from pyramid.security import authenticated_userid
from pyramid.url import route_url

import sqlalchemy.orm

def groupfinder(uid, request):
    """There are only two groups: 'editor' and 'admin'. The only difference
       is that only administrators can add users and edit certain files
       (like the logo and custom.css)."""
    if not uid:
        return None
    session = DBSession()
    user = session.query(User).get(uid)

    if not user:
        return None
    
    groups = ['group:editors']
    if user.admin:
        groups.append('group:admin')
    return groups
    

def login(request):
    """Returns a tuple of (authenticated) uid, and a message string.
    If the user could not be authenticated (or they didn't try), the uid
    will be None. If the user successfully logged in, sets a session
    cookie for this session."""
    
    session = DBSession()

    uid = authenticated_userid(request)
    if uid:
        return session.query(User).get(uid), None

    if 'user' in request.params and 'passwd' in request.params:
        uid = request.params['user']
        passwd = request.params['passwd']
        user = session.query(User).get(uid)
        if not user:
            return None, "Invalid user or password."

        if user.check_pw(passwd):
            headers = remember(request, uid)
            request.response.headerlist.extend(headers)
            return user, "Logged in Successfully"
        else:
            return None, "Invalid user or password."
    else:
        return None, None
