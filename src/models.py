from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50))
    
    referral_emails = db.relationship('Referrals', back_populates='user')

    def __repr__(self):
        return f'<Users {self.email}>'

    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username,
            'referral_emails': [x.email for x in self.referral_emails]
        }

class Referrals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    referral_id = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    
    user = db.relationship('Users', back_populates='referral_emails')

    def __repr__(self):
        return f'<Referrals {self.referral_id}>'