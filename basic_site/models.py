from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, DateTime, Integer, Boolean

from zope.sqlalchemy import ZopeTransactionExtension

from z3c.bcrypt import BcryptPasswordManager
manager = BcryptPasswordManager()

import sqlalchemy.orm

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = 'Users'
    uid = Column(String(10), primary_key=True)
    pw_hash = Column(String())
    fullname = Column(String())
    
    def __init__(self, name, pw, fullname):
        self.uid = name[:10]
        self.pw_hash = manager.encodePassword(pw)
        self.fullname = fullname

    def check_pw(self, passwd):
        return manager.checkPassword(self.pw_hash, passwd)

    def change_pw(self, old, new):
        """Verifies the old pw before changing it to new. Returns True if
    successful."""
        if manager.checkPassword(self.pw_hash, old):
            self.pw_hash = manager.encodePassword(pw)
            return True
        else:
            return False

class UserSession(Base):
    __tablename__ = 'Sessions'
    id = Column(String(), primary_key=True)
    last_used = Column(DateTime(), nullable=False)
    ip = Column(Integer(), nullable=False)
    user = Column(String(10), ForeignKey(User.uid))

    def __init__(self, ip):
        now = datetime.datetime.utcnow()
        md5 = hashlib.md5(ip)
        md5.update(randome.randint(1,0xffffffff))
        self.id = md5.hexdigest()
        self.last_used = now
        self.ip = ip

class Post(Base):
    __tablename__ = 'Post'
    id = Column(Integer(), primary_key=True)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    sticky = Column(Boolean(), nullable=False)
    contents = Column(String(), nullable=False)
    
    def __init__(self, creator, title, contents, sticky=False):
        if created:
            self.created = created
        else:
            self.created = datetime.datetime.utcnow()
        self.creator = creator
        self.sticky = sticky
        self.title = title[:30]
        self.contents = contents

    def edit(self, user, new_title, new_content):
        """Edit this post, and record the change in the history."""
        session = DBSession()
        hist = Post_History(user, self) 
        self.title = new_title[:30]
        self.content = new_content
        session.add(hist)

class Post_History(Base):
    id = Column(Integer(), nullable=False)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    sticky = Column(Boolean(), nullable=False)
    title = Column(String(30), nullable=False)
    contents = Column(String(), nullable=False)
    changed_by = Column(String(10), ForiegnKey(Users.uid), nullable=False)
    changed_on = Column(DateTime(), nullable=False)

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
                          .filter(Post.id = self.id)\
                          .one()
            post.edit(user, self.title, self.content)
        except sqlalchemy.orm.exc.NoResultFound:
            # Recreate it if it doesn't still exist
            post = Post(user, self.title, self.contents, self.created)
            session.add(page)
        session.flush()
 
class Page(Base):
    __tablename__ = 'Page'
    name = Column(String(15), primary_key=True)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    contents = Column(String(), nullable=False)
    
    def __init__(self, creator, name, contents, created=None):
        if created:
            self.created = created
        else:
            self.created = datetime.datetime.utcnow()
        self.name = name[:15]
        self.creator = creator
        self.contents = contents

    def edit(self, new_name, new_content, user):
        """Edit this post, and record the change in the history."""
        session = DBSession()
        hist = Page_History(user, self) 
        self.name = new_name
        self.content = new_content
        session.add(hist)

class Page_History(Base):
    name = Column(String(15), nullable=False)
    created = Column(DateTime(), nullable=False)
    creator = Column(String(10), nullable=False)
    contents = Column(String(), nullable=False)
    changed_by = Column(String(10), ForiegnKey(Users.uid), nullable=False)
    changed_on = Column(DateTime(), nullable=False)

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
                          .filter(Page.id = self.id)\
                          .one()
            page.edit(self.content, user)
        except sqlalchemy.orm.exc.NoResultFound:
            # Recreate it if it doesn't still exist
            page = Page(user, self.name, self.contents, self.created)
            session.add(page)
        session.flush() 
