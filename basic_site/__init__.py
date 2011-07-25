from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from basic_site.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    session_factory = UnencryptedCookieSessionFactoryConfig()
    config = Configurator(settings=settings, session_factory=session_factory)
    config.add_static_view('static', 'basic_site:static')
    config.add_route('Main', '/')
    config.add_view('basic_site.views.Main',
                    route_name='home',
                    renderer='templates/main.mako')
    return config.make_wsgi_app()

