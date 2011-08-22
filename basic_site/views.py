from basic_site.models import DBSession
from basic_site.models import Page, Post
from basic_site.security import groupfinder, login

import sqlalchemy.orm

from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget
from pyramid.url import route_url

def get_context(request):
    """Get the basic values all contexts should have, including
info on the logged in user and a list of pages."""
    context = get_context(request)

    session = DBSession()
    menu_pages = session.query(Page.id, Page.name)\
                        .order_by(Page.name)\
                        .all()
    context['menu_pages'] = menu_pages
    return context

def home(request):
    dbsession = DBSession()
 
    context = get_context(request)
   
    skip = request.matchdict.get('skip', 0)
 
    posts = dbsession.query(Post)\
                     .order_by(Post.created)\
                     .offset(skip)\
                     .limit(5)\
                     .all()

    context['posts'] = posts
    context['page_name'] = '*Main'
    context['page_subtitle'] = ''

    return context

def post(request):
    session = DBSession()

    context = get_context(request)
   
    hist = request.matchdict.has_key('hist')
    id = request.matchdict['id']
    context['page_name'] = 'View Post'
    context['page_subtitle'] = ''

    if hist:
        post = session.query(Post_History).get(id)
    else:
        post = session.query(Post).get(id)

    if not post:
        raise NotFound('No such post: %d' % id)
    
    context['posts'] = [post]
    return context

def page(request): 
    dbsession = DBSession()

    context = get_context(request)
    
    try:
        page = dbsession.query(Page)\
                        .filter(Page.name == request.matchdict['page'])\
                        .one()
    except sqlalchemy.orm.exc.NoResultFound:
        return exception_response(404)
   
    context['page'] = page
    context['page_name'] = page.name
    context['page_subtitle'] = '- %s' % page.name
    return context

def edit(request):
    context = get_context(request)

    ptype = request.matchdict['ptype']
    mode = request.matchdict['mode']
    id = request.matchdict.get('id')

    context.update({'ptype': ptype, 'mode': mode})

    if mode == 'add':
        return context

    context['id'] = id

    session = DBSession()
    
    tables = {('page', 'edit'): Page, ('page', 'revert'): Page_History,
              ('post', 'edit'): Post, ('post', 'revert'): Post_History}
    table = tables[(ptype, mode)]
    
    q = session.query(table)

    if mode == 'edit' and ptype == 'page': q = q.filter(table.name == id)
    elif mode == 'edit': q = q.filter(table.id == id)
    else: q= q.filter(table.hist_id == id)
    try:
        data = q.one()
    except:
        raise NotFound("No such %s to edit: %s" % (ptype, id))

    context['data'] = data
    return data

def get_required_params(params, args=[], kwargs=[]):
    """Get the required parameters, and return an args and kwargs 
    dictionary."""
    out_args = []
    out_kw = {}
    for p in args:
        if p not in params:
            raise KeyError("Missing param: %s" % p)
        out_args.append(params.getone())
    for p in kwargs:
        if p not in params:
            raise KeyError("Missing param: %s" % p)
        out_kw[p] = params.getone()
    return out_args, out_kw

def submit_content(request):
    """Handles page/post editing, adding, and restoration. The process is 
almost identical for pages and posts, so it's a unified view callable. It 
expects a 'ptypes' matchdict entry so that it can tell the difference 
though. """
    session = DBSession()
    context = get_context(request)

    ptype = request.matchdict['ptype']
    if ptype == 'page':
        table = Page
        hist_table = Page_History
        fields = ['title', 'content']
    else:
        table = Post
        hist_table = Post_History
        fields = ['name', 'content']
    
    args,_ = get_requested_params(request.params, fields) 
    if ptype == 'post':
        args.append( request.params.has_key('sticky') )

    if 'restore' in request.params:
        id = request.params.getone('id')
        hist_id = request.params.getone('restore')
        entry = session.query(table).get(id)
        if entry:
            # The post still exists, just updated it.
            args.append(uid)
            entry.edit(*args)
        else:
            # The post was deleted, make a new one and update the history
            # of the old one to point here.
            hist = session.query(hist_table).get(hist_id)
            if not hist:
                raise NotFound("Failure restoring %s(hist_id): %d" % \
                               (ptype, hist_id))
            
            args = [uid] + args + [hist.created]
            entry = table(*args)
            session.add(entry)
            session.query(hist_table)\
                   .filter(hist_table.id == id)\
                   .update({'id':entry.id})
        context['message'] = '%s restored succesfully.' % ptype.capitalize()
 
    elif 'id' in request.params:
        # Handle the editing of existing posts.
        id = request.params.getone()
        entry = session.query(table).get()
        if not entry:
            raise NotFound("No such %s to edit: %d" % (ptype, id))

        args.append(uid)
        entry.edit(*args)
        context['message'] = '%s edited succesfully.' % ptype.capitalize()
    else:
        args = [uid] + args
        entry = table(*args)
        session.add(entry)
        context['message'] = '%s added successfully.' % ptype.capitalize()
        
    session.flush()
    if ptype == 'post':
        context['page_name'] = 'View Post'
        context['page_subtitle'] = ''
        context['posts'] = [entry]
    else:
        context['page'] = entry
        context['page_name'] = entry.name
        context['page_subtitle'] = '- %s' % entry.name
    return context

def delete(request):
    session = DBSession()

    context = get_context(request)
    
    ptype = request.matchdict['ptype']
    if ptype == 'post':
        table = Post
        hist_table = Post_History
    else:
        table = Page
        hist_table = Page_History

    entry = session.query(table).get(request.matchdict['id'])
    title = entry.title if ptype == 'post' else entry.name
    hist = hist_table(entry)
    session.delete(entry)

    context['message'] = "Deleted %s: %s" % (ptype, title) 
    return context

def history(request):
    session = DBSession()

    context = get_context(request)

    ptype = request.matchdict('ptype')
    name = request.matchdict('id')
    if 'skip' in request.params:
        skip = request.params.getone('skip')
    else:
        skip = 0

    table = Page_History if ptype == 'page' else Post_History

    q = session.query(table)\
               .order_by(table.changed_on)
    if name != '*' and ptype == 'page': q = q.filter(table.name == id)
    if name != '*' and ptype == 'post': q = q.filter(table.name == id)

    context['count'] = q.count()
    context['skip'] = skip
    context['ptype'] = ptype
    context['id'] = id

    if skip:
        q = q.offset(skip)

    context['items'] = q.all()

    return context

def users(request):
    """Give a list of users."""

    session = DBSession()

    context = get_context(request)

    context['users'] = session.query(User).order_by(User.uid).all()
    return context

def mod_users(request):
    """This view handles adding, deleting, and editing users."""
    
    session = DBSession()

    context = get_context(request)

    action = request.matchdict['action']

    if action == 'add':
        n_uid = request.POST.getone('uid')
        passwd = request.POST.getone('passwd')
        repeat = request.POST.getone('repeat')
        fullname = request.POST.getone('fullname')
        admin = 'admin' in request.POST
        if session.query(User).get(n_uid):
            message = 'User %s already exists.' % n_uid
        else:
            try:
                if passwd != repeat:
                    raise ValueError("Passwords do not match.")
                user = User(n_uid, passwd, admin, fullname)
                session.add(user)
                message = "Added user %s" % user.uid
            except ValueError, msg:
                message = str(msg)
    else: 
        e_uid = request.matchdict['uid']
        user = session.query(User).get(e_uid)
        if not user:
            message = "User %s does not exist." % e_uid
        elif action == 'delete':
            if uid == 'admin':
                message = "Cannot delete the admin user."
            else:
                session.delete(user)
                message = "User %s deleted." % e_uid
        elif action == 'toggle_admin':
            user.admin = not user.admin
            session.flush()
            message = "User %s admin priviliges %s" %\
                            (e_uid, 'granted' if user.admin else 'revoked')

    request.GET['message'] = message
    return HTTPFound(location=request.route_url('users'), 
                     headers=request.headers)

def change_pw(request):
    session = DBSession()

    context = get_context(request)

    c_uid = request.matchdict['c_uid']
    if user and c_uid == user.uid:  
        old = request.POST.getone('old')
        new = request.POST.getone('new')
        repeat = request.POST.getone('repeat')
        if not user.check_pw(old):
            message = "Invalid password."
        elif new != repeat:
            message = "Passwords do not match." 
        else:
            user.change_pw(new)
            message = "Password changed"
    else:
         message = "No such user."

    request.GET['message'] = message
    return HTTPFound(location=request.route_url('users'), 
                     headers=request.headers)

def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('home'), 
                     headers=reqeust.headers)

def file(request):
    session = DBSession()
    response = request.response

    file_id = request.matchdict['file_id']
    file_info = session.query(File).get(file_id)
    if not file_info:
        raise NotFound("No such file: %s" % file_id)
    
