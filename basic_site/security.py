import datetime

from models import UserSession, User

class Auth:
    session_expire = datetime.timedelta(hours=2)
    def __init__(self, request):
        self.error = None
        self.user = None
        self.session = None
        self.ip = None

        if 'HTTP_COOKIE' in env: 
            try:
                cookie = request.cookie
            except:
                cookie = None
        else:
            cookie = None
        
        if cookie:
            sessionkey = cookie.get('session').value
        else:
            sessionkey = None
       
        ip = env.get('REMOTE_ADDR', 0)
        if ip:
            try:
                ip = ip.split('.')
                ip = map(int, ip)
                ip = ip[0] << 24 + ip[1] << 16 + ip[2] << 8 + ip[3]
            except:
                ip = 0
       
        if ip == 0:
            return

        if sessionkey:
            q = session.query(UserSession)\
                       .filter(UserSession.id == sessionkey)\
                       .filter(UserSession.ip == ip)\
                       .filter(UserSession.last_used >
                               (now - self.session_expire))
            try:
                user_sess = q.one()
            except:
                # Couldn't find a matching session
                sessionkey = None     

        # If they don't have a session key already, make them one. 
        if not sessionkey:
            user_sess = UserSession(ip)
            session.add(user_sess)
            self.ip = ip
            self.session = user_sess.id
            request.response.set_cookie('session', self.session)
            return

        q = session.query(UserSession)
        q.filter(UserSession.last_used < (now - self.session_expire))
        q.delete()

        # At this point, we should have a user_sess object and a 
        # session key. Now we'll check to see if the session key is logged in,
        # or if the user is trying to log in.
        request.response.set_cookie('session', self.session)
        self.session = sessionkey
        self.ip = ip
        user_sess.last_used = now
        session.commit()
        if user_sess.user:
            # Already logged in
            self.user = user_sess.user
            return

        # If they aren't trying to log in, we're done.
        if 'user' not in form or 'passwd' not in form:
            return

        uid = form.get_first('user')
        passwd = form.get_first('passwd')
        try:
            user = session.query(User).filter(User.uid = uid).one()
        except:
            self.error = "No such user: %s" % uid
            return

        if user.check_pw(passwd):
            self.user = uid
        else:
            self.error = "Invalid Password"

    def logged_in(self):
        return self.user is not None
