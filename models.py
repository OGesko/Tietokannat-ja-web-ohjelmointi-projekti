from app import db
from flask_login import UserMixin
from sqlalchemy import Sequence
from datetime import datetime

#create database tables
class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    accounts = db.relationship('Account', backref='user', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('username', name='uq_username'),
    )

    def __repr__(self):
        return '<User %r>' % self.username
    
class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    transactions = db.relationship('Transaction', backref='account', lazy=True)

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    transactions = db.relationship('TransactionCategory', backref='category', lazy=True)


class Transaction(db.Model):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, Sequence('transaction_id_seq'), primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    categories = db.relationship('TransactionCategory', backref='transaction', lazy=True)

class TransactionCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)