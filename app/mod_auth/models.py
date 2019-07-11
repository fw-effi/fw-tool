# Import the database object (db. from the main application module
from app import db, lm

# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

# Define a User model
class User(Base):
    __tablename__ = 'users'
    open_id = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

    def __init__(self, username, email, open_id):
        self.username = username
        self.email = email
        self.open_id = open_id

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))