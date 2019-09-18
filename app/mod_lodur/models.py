# Import the database object (db. from the main application module
from app import db

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

# 
alarmgroups = db.Table('alarmgroups',
    db.Column('alarmgroup_id', db.Integer, db.ForeignKey('AlarmGroup.id'), primary_key=True),
    db.Column('firefighter_id', db.Integer, db.ForeignKey('Firefighter.id'), primary_key=True)
)

# Define a Firebrigade Member
class Firefighter(Base):
    __tablename__ = 'Firefighter'
    uid = db.Column(db.Integer, unique=True, nullable=True) # Lodur Personalnummer
    grad = db.Column(db.String(64), nullable=False)
    vorname = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    mail = db.Column(db.String(64), nullable=False)
    alarmgroups = db.relationship('AlarmGroup', secondary=alarmgroups, lazy='subquery', backref=db.backref('alarmgroups', lazy=True))

    def __init__(self,uid,grad,vorname,name,mail):
        self.uid = uid
        self.grad = grad
        self.vorname = vorname
        self.name = name
        self.mail = mail
        

# Define alarmgroups
class AlarmGroup(Base):
    __tablename__ = 'AlarmGroup'
    name = db.Column(db.String(64), nullable=False)

    def __init__(self, username, email, open_id):
        self.username = username
        self.email = email
        self.open_id = open_id