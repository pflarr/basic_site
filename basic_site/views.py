from basic_site.models import DBSession, DEFAULT_ADMIN_PW
from basic_site.models import Post, Post_History, File, User
from basic_site.security import groupfinder, login

import mimetypes
import os

from pyramid.httpexceptions import HTTPFound, exception_response
from pyramid.exceptions import NotFound
from pyramid.security import forget
from pyramid.url import route_url

import sqlalchemy.orm
from sqlalchemy.sql import expression
import transaction

def get_context(request):
    """Get the basic values all contexts should have, including
info on the logged in user and a list of pages."""

    context = {}
    user, msg = login(request)
    if user is None and msg is None:
        session = DBSession()
        admin = session.query(User).get('admin')
    
    context['user'] = user
    # Get any messages passed in the query
    context['msg'] = [m for m in request.params.getall('msg')]
    if msg:
        context['msg'].append(msg)

    session = DBSession()
    menu_pages = session.query(Post.page)\
                        .filter(Post.page != 'Home')\
                        .order_by(Post.page)\
                        .group_by(Post.page)\
                        .all()
    context['menu_pages'] = menu_pages
    return context

def posts(request):
    dbsession = DBSession()
 
    context = get_context(request)
   
    skip = request.matchdict.get('skip', 0)
    if skip == '': skip = 0
    page = request.matchdict.get('page', 'Home')
 
    posts = dbsession.query(Post)\
                     .filter(Post.page == page)\
                     .order_by(Post.created)\
                     .offset(skip)\
                     .limit(5)\
                     .all()

    context['posts'] = posts
    context['page_name'] = page
    context['page_subtitle'] = ''

    return context

def post(request):
    session = DBSession()

    context = get_context(request)
   
    id = request.matchdict['id']
    page = request.matchdict['page']
    if '.' in id:
        id, version = id.split('.', 1)
    else:
        version = None

    
    try:
        id = int(id)
        if version: version = int(version)
    except ValueError:
        raise except_response(404)

    if version is not None:
        try:
            post = session.query(Post_History)\
                          .filter(Post_History.id == id)\
                          .filter(Post_History.page == page)\
                          .order_by(expression.desc(Post_History.changed_on))\
                          .limit(1)\
                          .offset(version)\
                          .one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise except_response(404)

        context['page_subtitle'] = 'Post %d History, rev %d' % (id, skip+1)
    else:
        post = session.query(Post).get(id)

        if not post:    
            raise NotFound('No such post: %d' % id)
    
        context['page_subtitle'] = 'Post %d' % id

    context['page_name'] = page

    hist_count = session.query(Post_History)\
                        .filter(Post_History.id == id)\
                        .count()
    if version is None and hist_count:
        context['prior'] = 0
    elif version is not None and (version+1) <= (hist_count-1):
        context['prior'] = version+1
    else:
        context['prior'] = None

    if version is not None:
        context['next'] = context['next'] = version - 1 

    context['post'] = post
    return context


def new_page(request):
    """Presents a form where the user can enter a new page name. When submitted
    with a page name, it redirects them to the add post form for that page."""
    if 'page' in request.params:
        page = request.params.getone('page')
        return HTTPFound(location=request.route_url('add', page=page))
    
    context = get_context(request)
    context['page_name'] = "*New Page"
    context['page_subtitle'] = ""
    return context

def edit(request):
    """Handle the edit view and submission of pages and posts."""
    context = get_context(request)

    mode = request.matched_route.name
    id = request.matchdict.get('id', None)
    page = request.matchdict.get('page', None)

    context['page_name'] = '*%s' % mode
    context['page_subtitle'] = ''

    context.update({'mode': mode})

    context['id'] = id
    context['page'] = page
    context['data'] = None

    if 'action' in request.POST:
        action = request.POST.getone('action')
    else:
        action = None

    if action == 'preview':
        if 'title' in request.POST:
            title = request.POST.getone('title')
        else:
            title = ''
            context['msg'].append("You might want to title your post.")
        if 'content' in request.POST:
            content = request.POST.getone('content')
        else:
            content = ''
            context['msg'].append('No content given')
        sticky = 'sticky' in request.POST
        post = Post(context['user'].uid, page, title, content, sticky)
        context['data'] = post
        context['preview'] = True
    elif action == 'submit':
        # Call the submit content view if we want to actually change something.
        return submit_content(request)

    if mode == 'edit' and action is None:
        # We aren't changing anything, just display the one we in intend
        # to change.
        session = DBSession()
        if mode == 'edit':
            table = Post
        else:
            table = Post_History
         
        q = session.query(table)
        q = q.filter(table.page == page)

        data = None
        if mode == 'edit': q = q.filter(table.id == id)
        else: q= q.filter(table.hist_id == id)
        
        try:
            data = q.one()
        except:
            raise NotFound("No such post to edit: %s" % id)

        context['data'] = data
        context['preview'] = False

    return context
        
def get_required_params(params, args=[], kwargs=[]):
    """Get the required parameters, and return an args and kwargs 
    dictionary."""
    out_args = []
    out_kw = {}
    for p in args:
        if p not in params:
            raise KeyError("Missing param: %s" % p)
        out_args.append(params.getone(p))
    for p in kwargs:
        if p not in params:
            raise KeyError("Missing param: %s" % p)
        out_kw[p] = params.getone(p)
    return out_args, out_kw

def submit_content(request):
    """Handles actually submitting new post content."""
    session = DBSession()
    context = get_context(request)
    uid = context['user'].uid

    mode = request.matched_route.name
   
    title = request.params.get('title')
    content = request.params.get('content') 
    sticky = request.params.has_key('sticky') 
    page = request.matchdict['page']

    if mode == 'edit':
        # Handle the editing of existing posts.
        id = request.matchdict['id']
        entry = session.query(Post).get(id)
        if not entry:
            raise NotFound("No such post to edit: %s, %d" % (page, id))

        hist = entry.edit(uid, title, content, sticky)
        session.add(hist)
        msg = 'Post edited succesfully.'
    elif mode == 'add':
        entry = Post(uid, page, title, content, sticky)
        session.add(entry)
        msg = 'Post added successfully.'
    else:
        msg = "Invalid mode: %s" % mode
        
    session.flush()
    
    context['msg'].append(msg)
    msgs = [('msg', m) for m in context['msg']]

    return HTTPFound(location=request.route_url('post', id=entry.id,
                                                page=page, _query=msgs))

def restore(request):
    """Restore a Post_History entry as the current version."""
    session = DBSession()
    context = get_context(request)
    uid = context['user'].uid

    id = request.matchdict['id']
    page = request.matchdict['page']
    version = request.matchdickt['version']

    try:
        entry = session.query(Post_History)\
                       .filter(Post_History.id == id)\
                       .filter(Post_History.page == page)\
                       .order_by(expression.desc(Post_History.changed_on))\
                       .limit(1)\
                       .offset(version)\
                       .one()
    except sqlalchemy.orm.exc.NoResultFound:
        return exception_response(404)

    current = session.query(Post).get(id)
    additions = entry.restore(context['user'], current)
    session.addall(additions)

    context['msg'].append('Post restored succesfully.')
    msgs = [('msg', m) for m in context['msg']]
    return HTTPFound(location=request.route_url('post', id=entry.id, page=page,
                                                _query=msgs))

def delete(request):
    session = DBSession()

    context = get_context(request)
   
    id = request.matchdict['id']
    page = request.matchdict['page'] 
    post = session.query(Post).get(id)
    title = post.title 
    hist = Post_History(context['uid'], post)
    session.delete(post)
    session.add(hist)

    context['msg'].append("Deleted Post: %s" % title)
    return context

def history(request):
    session = DBSession()

    context = get_context(request)

    id = request.matchdict('id')
    page = request.matchdict('page')

#XXX has a skip attribute that isn't used. Investigate.
    if 'skip' in request.params:
        skip = request.params.getone('skip')
    else:
        skip = 0

    q = session.query(Post)\
               .filter(Post.id == id)\
               .filter(Post.page == page)\
               .order_by(Post.changed_on)

    context['count'] = q.count()
    context['skip'] = skip
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
        context['msg'].append(message)
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
    rev = request.matchdict.get('rev', None)

    q = session.query(File).filter(File.name==name)\
                           .order_by(expression.desc(File.changed))\
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
    mime_type, encoding = mimetypes.guess_type(file_info.name)
    if 'get' in request.params or mime_type is None:
        response.content_disposition = 'attachment; filename="%s"' % \
                                        file_info.name
                                                    
    if mime_type:
        response.content_type = mime_type
    if encoding is not None:
        response.content_encoding
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
            context['msg'].append('File is too large.')
            transaction.abort()
        else:
            context['msg'].append('File submitted successfully.')
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
