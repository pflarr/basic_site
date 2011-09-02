from basic_site.models import DBSession, DEFAULT_ADMIN_PW
from basic_site.models import Page, Post, File, User
from basic_site.security import groupfinder, login

import os

from pyramid.httpexceptions import HTTPFound
from pyramid.exceptions import NotFound
from pyramid.security import forget
from pyramid.url import route_url

import sqlalchemy.orm
import transaction

def get_context(request):
    """Get the basic values all contexts should have, including
info on the logged in user and a list of pages."""

    context = {}
    user, msg = login(request)
    if user is None and msg is None:
        session = DBSession()
        admin = session.query(User).get('admin')
        if admin.check_pw(DEFAULT_ADMIN_PW):
            user = admin
            msg = "The default admin password is: '%s'. CHANGE IT! Until it "\
                  "is changed, all visitors are automatically admin." % \
                  DEFAULT_ADMIN_PW
    
    context['user'] = user
    context['message'] = msg

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
    """This view handles adding, deleting, and editing users."""
    
    session = DBSession()

    context = get_context(request)

    message = ''

    if 'action' in request.POST:
        action = request.POST.getone('action')
    else:
        action = None

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
                #transaction.commit()
            except ValueError, msg:
                message = str(msg)
    elif action == 'change_pw':
        user = context['user']
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
            session.add(user)

    elif action is not None: 
        e_uid = request.POST.getone('e_uid')
        user = session.query(User).get(e_uid)
        if not user:
            message = "User %s does not exist." % e_uid
        elif action == 'delete':
            if user.uid == 'admin':
                message = "Cannot delete the admin user."
            else:
                session.delete(user)
                message = "User %s deleted." % e_uid
                #transaction.commit()
        elif action == 'toggle_admin':
            if user.uid == 'admin':
                message = "The admin user is always an admin."
            else:
                user.admin = not user.admin
                session.flush()
                message = "User %s admin priviliges %s" %\
                            (e_uid, 'granted' if user.admin else 'revoked')
                #transaction.commit()

    if message:
        context['message'] = message
    context['users'] = session.query(User).order_by(User.uid).all()
    context['page_name'] = '*Users'
    context['page_subtitle'] = 'Manage Users'
    return context

def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('home'), 
                     headers=headers)

 
def file(request):
    session = DBSession()
    response = request.response

    name = request.matchdict['name']
    rev_tuple = request.matchdict['rev']
    try: 
        if len(rev_tuple) == 1:
            rev = int(rev_tuple[0])
        elif len(rev_tuple) > 1:
            raise ValueError
        else:
            rev = None
    except ValueError:
        raise NotFound("No such file.")

    q = session.query(File).filter(File.name==name)\
                           .order_by(File.changed)\
                           .limit(1)
    if rev:
        q = q.offset(rev)

    file_info = q.all()
    if not file_info:
        raise NotFound("No such file: %s" % name)

    file_info = file_info[0]
   
    path = os.path.join(request.registry.settings['file_path'], 
                        str(file_info.id))
    try:
        file = open(path)
    except:
        raise NotFound("No such file (though it should exist).")

    response = request.response
    response.app_iter = file
    return response

# Limit files to 64 MBytes
FILE_SIZE_LIMIT = 1 << 26
def files(request):
    session = DBSession()
    context = get_context(request)
    context['page_name'] = '*Files'
    context['page_subtitle'] = 'List of uploaded files'

    if 'data' in request.POST:
        field = request.POST.getone('data')
        name = field.filename
        if '\\' in name:
            name = name.split('\\')[-1]
        if '/'in name:
            name = name.split('/')[-1]

        file = File(name, context['user'].uid)
        session.add(file)
        session.flush()
        path = os.path.join(request.registry.settings['file_path'], 
                            str(file.id))

        out_file = open(path,'w')
        field.file.seek(0)
        data = field.file.read(1<<16)
        total_size = len(data)
        while data and total_size < FILE_SIZE_LIMIT:
            out_file.write(data)
            data = field.file.read(1<<16)
            total_size += len(data)
        out_file.close()

        file.size = total_size
        session.add(file)
        session.flush()

        if total_size > FILE_SIZE_LIMIT:
            # We limit the size of files, just in case.
            os.remove(path)
            context['message'] = 'File is too large.'
            transaction.abort()
        else:
            context['message'] = 'File submitted successfully.'
            #transaction.commit()
       

    files = session.query(File)
    files_by_name = {}
    for file in files:
        file_list = files_by_name.get(file.name, [])
        file_list.append(file)
        files_by_name[file.name] = file_list

    for file_list in files_by_name.values():
        file_list.sort(lambda a,b: cmp(a.changed, b.changed))

    context['files'] = files_by_name

    return context
