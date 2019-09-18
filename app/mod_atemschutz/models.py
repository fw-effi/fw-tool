# Import the database object (db. from the main application module
from app import db

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

# Define a AS-Event
class Event(Base):
    __tablename__ = 'AS-Event'
    name = db.Column(db.String(64), nullable=False, unique=True)
    category = db.Relation
    date = db.Column(db.String(64), nullable=True)

    def __init__(self, username, email, open_id):
        self.username = username
        self.email = email
        self.open_id = open_id