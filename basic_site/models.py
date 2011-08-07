from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, DateTime, Integer, Boolean

from zope.sqlalchemy import ZopeTransactionExtension

from z3c.bcrypt import BcryptPasswordManager
manager = BcryptPasswordManager()

from pyramid.security import Allow, Everyone

import sqlalchemy.orm

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:editors', 'edit'),
                (Allow, 'group:admin', 'admin') ]
    def __init__(self, request):
        pass

class User(Base):
    __tablename__ = 'Users'
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
        """Verifies the old pw before changing it to new. Returns True if
    successful."""
        self.pw_hash = manager.encodePassword(pw)

class Post(Base):
    __tablename__ = 'Post'
    id = Column(Integer(), primary_key=True)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    sticky = Column(Boolean(), nullable=False)
    contents = Column(String(), nullable=False)
    
    def __init__(self, creator, title, contents, sticky=False, created=None):
        if created:
            self.created = created
        else:
            self.created = datetime.datetime.utcnow()
        self.creator = creator
        self.sticky = sticky
        self.title = title[:30]
        self.contents = contents

    def edit(self, title, content, sticky, user):
        """Edit this post, and record the change in the history."""
        session = DBSession()
        hist = Post_History(user, self) 
        self.title = title[:30]
        self.content = content
        self.sticky = sticky
        session.add(hist)

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
    contents = Column(String(), nullable=False)

    def __init__(self, editor_uid, post):
        for col in post.__table__.c:
            self.__table__[col] = post.__table__.c[col]
        self.changed_by = editor_uid
        self.changed_on = datetime.datetime.utcnow()

    def restore(self, user):
        """Restore this history item's content."""
        session = DBSession()
        try:
            post = session.query(Post)\
                          .filter(Post.id == self.id)\
                          .one()
            post.edit(user, self.title, self.content)
        except sqlalchemy.orm.exc.NoResultFound:
            # Recreate it if it doesn't still exist
            post = Post(user, self.title, self.contents, self.created)
            session.add(page)
        session.flush()
 
class Page(Base):
    __tablename__ = 'Page'
    id = Column(Integer(), primary_key=True)
    name = Column(String(15), unique=True)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    contents = Column(String(), nullable=False)

    allowed_chars = ['abcdefghijklmnopqrstuvwxyz0123456789 _-'] 
    def __init__(self, creator, name, contents, created=None):
        if created:
            self.created = created
        else:
            self.created = datetime.datetime.utcnow()

        self.name = ''.join([c if c.lower() in self.allowed_chars else '_'
                               for c in name[:15]])
        self.creator = creator
        self.contents = contents

    def edit(self, name, content, user):
        """Edit this post, and record the change in the history."""
        session = DBSession()
        hist = Page_History(user, self) 
        self.name = name
        self.content = content
        session.add(hist)

class Page_History(Base):
    __tablename__ = 'page_history'
    hist_id = Column(Integer(), primary_key=True)
    id = Column(Integer(), nullable=False)
    name = Column(String(15), nullable=False)
    changed_on = Column(DateTime(), nullable=False)
    changed_by = Column(String(10), ForeignKey(User.uid), nullable=False)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    contents = Column(String(), nullable=False)

    def __init__(self, editor_uid, page):
        for col in page.__table__.c:
            self.__table__[col] = page.__table__.c[col]
        self.changed_by = editor_uid
        self.changed_on = datetime.datetime.utcnow()

    def restore(self, user):
        """Restore this history item's content."""
        session = DBSession()
        try:
            page = session.query(Page)\
                          .filter(Page.id == self.id)\
                          .one()
            page.edit(self.content, user)
        except sqlalchemy.orm.exc.NoResultFound:
            # Recreate it if it doesn't still exist
            page = Page(user, self.name, self.contents, self.created)
            session.add(page)
        session.flush() 
