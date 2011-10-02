from creole import Parser
from creole.html_emitter import HtmlEmitter

import datetime

from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.types import String, DateTime, Integer, Boolean

from pyramid.security import Allow, Everyone
import transaction

from zope.sqlalchemy import ZopeTransactionExtension

from z3c.bcrypt import BcryptPasswordManager
manager = BcryptPasswordManager()

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class BS_Emitter(HtmlEmitter):
    pass

DEFAULT_ADMIN_PW = 'change_this!'
def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    session = DBSession()
    admin = session.query(User).get('admin')
    if not admin:
        admin = User('admin', DEFAULT_ADMIN_PW, True, 'Admin')
        session.add(admin)
        session.flush()
        transaction.commit()

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:editors', 'edit'),
                (Allow, 'group:admin', 'admin') ]
    def __init__(self, request):
        pass

class User(Base):
    __tablename__ = 'users'
    uid = Column(String(10), primary_key=True)
    pw_hash = Column(String(), nullable=False)
    admin = Column(Boolean(), nullable=False)
    fullname = Column(String(), nullable=False)

    UID_CHARS = 'abcdefghijklmnopqrstuvwxyz1234567890_-'
    
    def __init__(self, uid, pw, admin, fullname):
        if len(uid) > 10 or \
           all(c.lower() not in self.UID_CHARS for c in uid):
            raise ValueError("Invalid User name: %s")
        self.uid = uid
        self.pw_hash = manager.encodePassword(pw)
        self.admin = admin 
        self.fullname = fullname

    def check_pw(self, passwd):
        return manager.checkPassword(self.pw_hash, passwd)

    def change_pw(self, new):
        self.pw_hash = manager.encodePassword(new)

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer(), primary_key=True)
    title = Column(String(30), nullable=False)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    sticky = Column(Boolean(), nullable=False)
    content = Column(String(), nullable=False)
    
    def __init__(self, creator, title, content, sticky=False, created=None):
        if created:
            self.created = created
        else:
            self.created = datetime.datetime.utcnow()
        self.creator = creator
        self.sticky = sticky
        self.title = title[:30]
        self.content = content

    def edit(self, user, title, content, sticky, created=None):
        """Edit this post, and return the history row (will need to be
    added to a session.)"""
        hist = Post_History(user, self) 
        self.title = title[:30]
        self.content = content
        self.sticky = sticky
        if created is None:
           self.created = datetime.datetime.utcnow()
        else:
            self.created = created
        return hist

    def render(self):
        doc = Parser(self.content).parse()
        return BS_Emitter(doc).emit()
        
class Post_History(Base):
    __tablename__ = 'post_history'
    hist_id = Column(Integer(), primary_key=True)
    id = Column(Integer(), nullable=False)
    changed_on = Column(DateTime(), nullable=False)
    changed_by = Column(String(10), ForeignKey(User.uid), nullable=False)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    sticky = Column(Boolean(), nullable=False)
    title = Column(String(30), nullable=False)
    content = Column(String(), nullable=False)

    def __init__(self, editor_uid, post):
        self.id = post.id
        self.title = post.title
        self.created = post.created
        self.creator = post.creator
        self.sticky = post.sticky
        self.content = post.content
        self.changed_by = editor_uid
        self.changed_on = datetime.datetime.utcnow()

    def restore(self, user):
        """Restore this history item's content. Returns an item to add to
    the db/session."""
        if current:
            return current.edit(user, self.title, self.content, self.sticky,
                                created=self.created)
        else:
            return Post(user, self.title, self.content, self.sticky,
                        self.created)
    
    def render(self):
        doc = Parser(self.content).parse()
        return BS_Emitter(doc).emit()

 
class Page(Base):
    __tablename__ = 'pages'
    id = Column(Integer(), primary_key=True)
    name = Column(String(15), unique=True)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    content = Column(String(), nullable=False)

    allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789 _-'
    def __init__(self, creator, name, content, created=None):
        if created:
            self.created = created
        else:
            self.created = datetime.datetime.utcnow()

        self.name = ''.join([c if c.lower() in self.allowed_chars else '_'
                               for c in name[:15]])
        self.creator = creator
        self.content = content

    def edit(self, user, name, content, created=None):
        """Edit this page, and return the history table entry."""
        hist = Page_History(user, self) 
        self.name = name
        self.content = content
        if created:
            self.created = datetime.datetime.utcnow()
        else:
            self.created = created
        return hist

    def render(self):
        doc = Parser(self.content).parse()
        return BS_Emitter(doc).emit()

class Page_History(Base):
    __tablename__ = 'page_history'
    hist_id = Column(Integer(), primary_key=True)
    id = Column(Integer(), nullable=False)
    name = Column(String(15), nullable=False)
    changed_on = Column(DateTime(), nullable=False)
    changed_by = Column(String(10), ForeignKey(User.uid), nullable=False)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    content = Column(String(), nullable=False)

    def __init__(self, editor_uid, page):
        self.id = page.id
        self.name = page.name
        self.created = page.created
        self.creator = page.creator
        self.content = page.content
        self.changed_by = editor_uid
        self.changed_on = datetime.datetime.utcnow()

    def restore(self, user, current):
        """Restore this history item's content, returns a list of rows to
    add to the session."""
        
        if current:
            return current.edit(user, self.name, self.content, self.created)
        else:
            return Page(user, self.name, self.content, self.created)

    def render(self):
        doc = Parser(self.content).parse()
        return BS_Emitter(doc).emit()

class File(Base):
    __tablename__ = 'files';
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    submitter = Column(String, nullable=False)
    changed = Column(DateTime, nullable=False)
    size = Column(Integer)

    def __init__(self, name, submitter):
        self.name = name
        self.submitter = submitter
        self.changed = datetime.datetime.now()

if __name__ == '__main__':
    from sqlalchemy import engine_from_config
    from ConfigParser import SafeConfigParser
    import sys
    p = SafeConfigParser()
    assert p.read(sys.argv[1]), "Bad path to config (arg1): %s" % sys.argv[1]
    
    engine = engine_from_config(p._sections['app:basic_site'])
    initialize_sql(engine)
    engine = engine_from_config
