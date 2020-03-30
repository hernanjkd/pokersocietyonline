from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50))
    referral_id = db.Column(db.String(10), default=None)
    payment_types = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Users {self.email}>'


class Referrals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referral_id = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<Referrals {self.referral_id}>'