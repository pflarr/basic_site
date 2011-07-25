from basic_site.models import DBSession
from basic_site.models import Pages, Posts
from basic_site.auth import Auth

import sqlalchemy.orm

def Main(request):
    dbsession = DBSession()
    
    context = {'auth': Auth(request)}
   
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

def Page(request): 
    dbsession = DBSession()

    context = {'auth': Auth(request)}
    
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
