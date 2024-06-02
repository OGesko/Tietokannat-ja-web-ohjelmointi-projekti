from app import db
from flask_login import UserMixin
from sqlalchemy import Sequence

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=False)

    __table_args__ = (
        db.UniqueConstraint('username', name='uq_username'),
    )

    def __repr__(self):
        return '<User %r>' % self.username