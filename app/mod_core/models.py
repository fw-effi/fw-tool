# Import the database object (db. from the main application module
from app import db, auth_module
from time import time
from app.mod_auth.models import auth_groups, auth_roles

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean, default=0,nullable=True)   

    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d                                    

# Define Notification Recipients
class notifications_recipients(Base):
    __tablename__ = 'Notifications_recipients'
    auth_user_id = db.Column(db.Integer(), db.ForeignKey("Auth_users.id"))
    notify_category_id = db.Column(db.Integer(), db.ForeignKey("Notifications_category.id"))
    
# Define Notification Category
class notifications_category(Base):
    __tablename__ = 'Notifications_category'  
    name = db.Column(db.String(64), nullable=True)
    beschreibung = db.Column(db.String(64), nullable=False)
    recipients = db.relationship('User', secondary='Notifications_recipients', lazy='subquery', backref=db.backref('notification_categories', lazy=True))

    def __init__(self,name,beschreibung):
        self.name = name
        self.beschreibung = beschreibung

# Define Notification Messages
class notifications_messages(Base):
    __tablename__ = 'Notifications_messages'
    user_id = db.Column(db.Integer, db.ForeignKey('Auth_users.id'))
    payload_json = db.Column(db.Text)
    url = db.Column(db.String(64), nullable=True)
    type = db.Column(db.String(64), default='Information')

    def __init__(self,user_id,created_at,payload_json,url):
        self.user_id = user_id
        self.created_at = created_at
        self.payload_json = payload_json
        self.url = url
    
    def get_data(self):
        return json.loads(str(self.payload_json))