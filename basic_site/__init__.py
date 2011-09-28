from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from basic_site.security import groupfinder

from basic_site.models import initialize_sql, RootFactory

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    session_factory = UnencryptedCookieSessionFactoryConfig(
                                                    settings['sess_secret'])
    authn_policy = AuthTktAuthenticationPolicy(settings['auth_secret'],
                                               callback=groupfinder,
                                               include_ip=True,
                                               timeout=60*60*1,
                                               reissue_time=60*6)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, 
                          session_factory=session_factory,
                          root_factory=RootFactory,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.add_static_view('static', 'basic_site:static')
    config.add_route('home', '')
    config.add_view('basic_site.views.home',
                    route_name='home',
                    renderer='basic_site:templates/main.mako')
    config.add_route('post','post/{id:\d+}')
    config.add_view('basic_site.views.post', route_name='post',
                    renderer='basic_site:templates/post.mako')
    config.add_route('page', 'page/{name}')
    config.add_view('basic_site.views.page', route_name='page',
                    renderer='basic_site:templates/page.mako')
    config.add_route('add', '{mode:add}/{ptype:(page|post)}')
    config.add_route('edit', '{mode:edit}/{ptype:(page|post)}/{id}')
    config.add_view('basic_site.views.edit', route_name='add',
                    renderer='basic_site:templates/edit.mako')
    config.add_view('basic_site.views.edit', route_name='edit',
                    renderer='basic_site:templates/edit.mako')
    config.add_route('users', 'users')
    config.add_view('basic_site.views.users', route_name='users',
                    renderer='basic_site:templates/users.mako')
    config.add_route('file_rev', 'file/{rev}/{name}')
    config.add_route('file', 'file/{name}')
    config.add_view('basic_site.views.file', route_name='file')
    config.add_view('basic_site.views.file', route_name='file_rev')
    config.add_route('files', 'files/')
    config.add_view('basic_site.views.files', route_name='files',
                    renderer='basic_site:templates/files.mako')
    config.add_route('logout', 'logout/')
    config.add_view('basic_site.views.logout', route_name='logout')
    return config.make_wsgi_app()

