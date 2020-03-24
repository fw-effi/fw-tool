# Import the database object (db. from the main application module
from app import db, auth_module

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
    
# Define Category
class Category(Base):
    __tablename__ = 'AS_Category'
    name = db.Column(db.String(64), nullable=False, unique=True)
    training = db.Column(db.Boolean, default=False, nullable=True)
    def __init__(self,name,training):
        self.name = name
        self.training = training

# Define a AS-Entry
class Entry(Base):
    __tablename__ = 'AS_Entry'
    time = db.Column(db.Integer,nullable=False,default=0)
    member = db.relationship("Firefighter", backref=db.backref('as_entries',lazy=True))
    member_id = db.Column(db.Integer, db.ForeignKey('Firefighter.id'))
    datum = db.Column(db.DateTime,nullable=False)
    category = db.relationship("Category", backref=db.backref('entries',lazy=True))
    category_id = db.Column(db.Integer, db.ForeignKey('AS_Category.id'))

    def __init__(self, member_id,datum,category_id, time):
        self.member_id = member_id
        self.datum = datum
        self.category_id = category_id
        self.time = time