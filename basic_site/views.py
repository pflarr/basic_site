from basic_site.models import DBSession
from basic_site.models import Page, Post
from basic_site.security import groupfinder, login

import sqlalchemy.orm

from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget
from pyramid.url import route_url

def home(request):
    dbsession = DBSession()
  
    uid, login_msg = login(request)
    context = {'uid': uid, 
               'login_msg': login_msg}
   
    skip = request.matchdict.get('skip', 0)
 
    posts = dbsession.query(Post)\
                     .order_by(Post.created)\
                     .skip(skip)\
                     .limit(5)\
                     .all()

    context['posts'] = posts
    context['page_name'] = '*Main'
    context['page_subtitle'] = ''

    return context

def post(request):
    session = DBSession()

    uid, login_msg = login(request)
    context = {'uid': uid, 
               'login_msg': login_msg}
   
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

    uid, login_msg = login(request)
    context = {'uid': uid, 
               'login_msg': login_msg}
    
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
    uid, login_msg = login(request)
    context = {'uid': uid, 
               'login_msg': login_msg}

    ptype = request.matchdict['ptype']
    mode = request.matchdict['mode']
    id = request.matchdict.get('id')

    context = {'ptype': ptype, 'mode': mode}

    if mode == 'add':
        return context

    context['id'] = id

    session = DBSession()
    
    tables = {('page', 'edit'): Page, ('page', 'revert'): Page_History,
              ('post', 'edit'): Post, ('post', 'revert'): Post_History)}
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

def submit_post(request):
    session = DBSession()
    uid, login_msg = login(request)
    context = {'uid': uid, 
               'login_msg': login_msg}
    
    args,_ = get_requested_params(request.params, ['title', 'content']) 
    args.append( request.params.has_key('sticky') )

    if 'restore' in request.params:
        id = request.params.getone('id')
        hist_id = request.params.getone('restore')
        post = session.query(Post).get(id)
        if post:
            # The post still exists, just updated it.
            args.append(uid)
            post.edit(*args)
        else:
            # The post was deleted, make a new one and update the history
            # of the old one to point here.
            hist = session.query(Post_History).get(hist_id)
            if not hist:
                raise NotFound("Failure restoring post(hist_id): %d" % hist_id)
            
            args = [uid] + args + [hist.created]
            post = Post(*args)
            session.add(post)
            session.query(Post_History)\
                   .filter(Post_History.id == id)\
                   .update({'id':post.id})
        context['message'] = 'Post restored succesfully.'
 
    elif 'id' in request.params:
        # Handle the editing of existing posts.
        id = request.params.getone()
        post = session.query(Post).get()
        if not post:
            raise NotFound("No such post to edit: %d" % id)

        args.append(uid)
        post.edit(*args)
    except:
        context['message'] = 'Post edited succesfully.'
    else:
        args = [uid] + args
        post = Post(*args)
        session.add(post)
        context['message'] = 'Post added successfully.'
        
    session.flush()
    context['page_name'] = 'View Post'
    context['page_subtitle'] = ''
    context['posts'] = [post]
    return context

def submit_page(request):
    """Create, edit, and restore submitted pages."""
    session = DBSession()
    uid, login_msg = login(request)
    context = {'uid': uid, 
               'login_msg': login_msg}
   
    args,_ = get_requested_params(request.params, ['name', 'content'])

    if 'restore' in request.params:
        id = request.params.getone('id')
        hist_id = request.params.getone('restore')
        post = session.query(Post).get(id)
        if post:
            # The post still exists, just updated it.
            args.append(uid)
            post.edit(*args)
        else:
            # The post was deleted, make a new one and update the history
            # of the old one to point here.
            hist = session.query(Post_History).get(hist_id)
            if not hist:
                raise NotFound("Failure restoring post(hist_id): %d" % hist_id)
            
            args = [uid] + args + [hist.created]
            post = Post(*args)
            session.add(post)
            session.query(Post_History)\
                   .filter(Post_History.id == id)\
                   .update({'id':post.id})
        context['message'] = 'Post restored succesfully.'
 
    elif 'id' in request.params:
        # Handle the editing of existing posts.
        id = request.params.getone()
        post = session.query(Post).get()
        if not post:
            raise NotFound("No such post to edit: %d" % id)

        args.append(uid)
        post.edit(*args)
    except:
        context['message'] = 'Post edited succesfully.'
    else:
        args = [uid] + args
        post = Post(*args)
        session.add(post)
        context['message'] = 'Post added successfully.'
        
    session.flush()
    context['page_name'] = 'View Post'
    context['page_subtitle'] = ''
    context['posts'] = [post]
    return context

def history(request):
    session = DBSession()

    uid, login_msg = login(request)
    context = {'uid': uid, 
               'login_msg': login_msg}

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



def logout(request):
    headers = forget(request)
    return HTTPFound(location=route_url('home', request), headers=headers)
