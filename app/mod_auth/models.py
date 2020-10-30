import typing
# Import the database object (db. from the main application module
from app import db
from time import time

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
    
    def __repr__(self) -> str:
        return self._repr(id=self.id)

    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except sa.orm.exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"

# Define a User model
class User(Base):
    __tablename__ = 'Auth_users'
    open_id = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    notification_lastread = db.Column(db.DateTime, nullable=True)
    #notifications = db.relationship('Notifications_category', secondary="Notifications_recipients", lazy='subquery', backref=db.backref('recipients', lazy=True))

    def __init__(self, username, email, open_id):
        self.username = username
        self.email = email
        self.open_id = open_id

# Define User Role association model
class auth_grouprole(Base):
    __tablename__ = 'Auth_grouprole'
    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey('Auth_roles.id'))
    group_id = db.Column(db.Integer(), db.ForeignKey('Auth_groups.id'))

# Define Permission Roles model -> imported from Lodur
class auth_roles(Base):
    __tablename__ = 'Auth_roles'
    name = db.Column(db.String(64), nullable=False, unique=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=0)
    groups = db.relationship('auth_groups', secondary="Auth_grouprole", lazy='subquery', backref=db.backref('roles', lazy=True))

    def __init__(self,name):
        self.is_deleted = 0
        self.name = name
    
    def __repr__(self):
        return self._repr(id=self.id,
            name=self.name
        )

# Define Permission Groups model
class auth_groups(Base):
    __tablename__ = 'Auth_groups'

    name = db.Column(db.String(64), nullable=False, unique=True)
    beschreibung = db.Column(db.String(64), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=0)
    #roles = db.relationship('Auth_roles', secondary=Auth_grouprole, lazy='subquery', backref=db.backref('groups', lazy=True))
    

    def __init__(self,name,beschreibung):
        self.is_deleted = 0
        self.name = name
        self.beschreibung = beschreibung

