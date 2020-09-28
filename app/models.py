from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True, unique=True)
    scrip = db.Column(db.String(20), index=True, unique=True)
    sector = db.Column(db.String(50), index=True)
    ticker = db.Column(db.Integer, index=True, unique=True)
    ss_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Company {}>'.format(self.name)


class PriceHistory(db.Model):
    __tablename__ = "price_history"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), index=True)
    company = db.Column(db.String(200), ForeignKey('companies.name'), index=True)
    no_of_txns = db.Column(db.Integer)
    max_price = db.Column(db.DECIMAL(10, 2))
    min_price = db.Column(db.DECIMAL(10, 2))
    closing_price = db.Column(db.DECIMAL(10, 2))
    traded_shares = db.Column(db.Integer)
    amount = db.Column(db.DECIMAL(15, 2))
    previous_closing = db.Column(db.DECIMAL(10, 2))
    difference = db.Column(db.DECIMAL(10, 2))
    company_model = relationship("Company", lazy='joined')

    def __repr__(self):
        return '<Pricehistory {date},{company},{closing_price}>'.format(self.name)


class TransactionHistory(db.Model):
    __tablename__ = "transactions_history"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), index=True)
    contract_number = db.Column(db.BIGINT, index=True)
    symbol = db.Column(db.String(20), index=True)
    buyer_broker = db.Column(db.Integer)
    seller_broker = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    rate = db.Column(db.DECIMAL(10, 2))
    amount = db.Column(db.DECIMAL(15, 2))

    def __repr__(self):
        return '<TransactionHistory {date},{company},>'.format(self.name)
