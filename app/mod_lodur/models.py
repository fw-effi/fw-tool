import typing

# Import the database object (db. from the main application module
from app import db

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean, default=0,nullable=True)
    
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

# 
alarmgroups = db.Table('alarmgroups',
    db.Column('alarmgroup_id', db.Integer, db.ForeignKey('AlarmGroup.id'), primary_key=True),
    db.Column('firefighter_id', db.Integer, db.ForeignKey('Firefighter.id'), primary_key=True)
)
FF_Zugmapping = db.Table('FF_Zugmapping',
    db.Column('ff_zug_id', db.Integer, db.ForeignKey('FF_Zug.id'), primary_key=True),
    db.Column('firefighter_id', db.Integer, db.ForeignKey('Firefighter.id'), primary_key=True)
)


# Define a Firebrigade Member
class Firefighter(Base):
    __tablename__ = 'Firefighter'
    uid = db.Column(db.Integer, unique=True, nullable=True) # ILEF Personalnummer
    sync_uid = db.Column(db.Integer, nullable=True) # Wird bei jedem Sync überschrieben und geprüft ob der Datensatz aktualisiert wurde
    last_sync = db.Column(db.DateTime, nullable=True)
    grad = db.Column(db.String(64), nullable=False)
    grad_sort = db.Column(db.Integer,nullable=True)
    vorname = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    mail = db.Column(db.String(64), nullable=False)
    eintritt = db.Column(db.DateTime, nullable=True)
    zug = db.relationship('FF_Zug', secondary=FF_Zugmapping, lazy='subquery', backref=db.backref('members', lazy=True))
    alarmgroups = db.relationship('AlarmGroup', secondary=alarmgroups, lazy='subquery', backref=db.backref('members', lazy=True))

    def __init__(self,uid,grad,grad_sort,vorname,name,mail,eintritt,sync_uid, last_sync):
        self.uid = uid
        self.grad = grad
        self.grad_sort = grad_sort
        self.vorname = vorname
        self.name = name
        self.mail = mail
        self.eintritt = eintritt
        self.sync_uid = sync_uid
        self.last_sync = last_sync
    
    def __repr__(self):
        return self._repr(id=self.id,
            name=self.name,
            vorname=self.vorname,
            grad=self.grad,
            grad_sort=self.grad_sort,
            mail=self.mail,
            zug=self.zug,
            eintritt=self.eintritt,
            last_sync=self.last_sync
        )

# Define alarmgroups
class AlarmGroup(Base):
    __tablename__ = 'AlarmGroup'
    name = db.Column(db.String(64), nullable=False)
    firefighters = db.relationship('Firefighter', secondary=alarmgroups, lazy='subquery',backref=db.backref('firefighters',lazy=True))

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return self._repr(id=self.id,name=self.name)

# Define Firefighter Zugseinteilung
class FF_Zug(Base):
    __tablename__ = 'FF_Zug'
    name = db.Column(db.String(64), nullable=False)
    firefighters = db.relationship('Firefighter', secondary=FF_Zugmapping, lazy='subquery',backref=db.backref('members',lazy=True))

    def __repr__(self):
        return self._repr(name=self.name)

# Define General Lodur Table
class Lodur_General(Base):
    __tablename__ = 'Lodur_general'
    name = db.Column(db.String(64), nullable=True)
    value = db.Column(db.String(64), nullable=True)

    def __init__(self,name,value):
        self.name = name
        self.value = value