# Import the database object (db. from the main application module
from app import db, auth_module


# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())


# Define general Information
class GVZupdate(Base):
    __tablename__ = 'Alarm_GVZupdate'
    einsatzbereit = db.Column(db.Boolean, nullable=False)
    anzahlFahrer = db.Column(db.Integer,default=0, nullable=True)
    mat_ready = db.Column(db.Boolean, nullable=True)
    mat_dringend = db.Column(db.String(64),nullable=True)
    rd_fahrer = db.Column(db.Boolean, nullable=True)

    def __init__(self,einsatzbereit,anzahlFahrer,mat_ready,mat_dringend,rd_fahrer):
        self.einsatzbereit = einsatzbereit
        self.anzahlFahrer = anzahlFahrer
        self.mat_ready = mat_ready
        self.mat_dringend = mat_dringend
        self.rd_fahrer = rd_fahrer


# Define notAvailable AdFs
class GVZnotAvailable(Base):
    __tablename__ = 'Alarm_GVZnotAvailable'
    member = db.relationship("Firefighter", backref=db.backref('Alarm_GVZnotAvailable',lazy=True))
    member_id = db.Column(db.Integer, db.ForeignKey('Firefighter.id'))
    isDriver = db.Column(db.Boolean, nullable=True)
    isKader = db.Column(db.Boolean, nullable=True)
    datumvon = db.Column(db.DateTime,nullable=True)
    datumbis = db.Column(db.DateTime,nullable=True)
    art = db.Column(db.String(64),nullable=True)
    reportedby = db.Column(db.String(64),nullable=True)

    def __init__(self,member_id,datumvon,datumbis,art,isDriver,isKader,reportedby):
        self.member_id = member_id
        self.datumvon = datumvon
        self.datumbis = datumbis
        self.art = art
        self.isDriver = isDriver
        self.isKader = isKader
        self.reportedby = reportedby


class pushCategory(Base):
    __tablename__ = "Alarm_PushCategory"
    name = db.Column(db.String(64), nullable=True)
    tag = db.Column(db.String(64), nullable=True)

    def __init__(self, name, tag):
        self.name = name
        self.tag = tag


class pushEntry(Base):
    __tablename__ = "Alarm_PushEntry"
    selector = db.Column(db.String(64), nullable=True)
    message = db.Column(db.String(256), nullable=True)
    category = db.relationship("pushCategory", backref=db.backref('entries', lazy=True))
    category_id = db.Column(db.Integer, db.ForeignKey('Alarm_PushCategory.id'))

    def __init__(self, selector, message, category_id):
        self.selector = selector
        self.message = message
        self.category_id = category_id
