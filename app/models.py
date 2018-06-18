from app import db, login
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return Doctor.query.get(int(id))

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(128), index= True, unique = True)
    password_hash = db.Column(db.String(128))
    patients = db.relationship('Patient', backref = 'doctor', lazy = 'dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Doctor {}>'.format(self.username)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True)
    age = db.Column(db.Integer)
    email = db.Column(db.String(128), unique = True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))

    def avatar(self, size):
        #if self.email is None:
        digest = md5('josh@gmail.com'.encode('utf-8')).hexdigest()
        #else:
        #    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def __repr__(self):
        return 'Patient {}'.format(self.name)
