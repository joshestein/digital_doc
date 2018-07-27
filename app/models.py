from app import db, login
from datetime import datetime
from flask_login import UserMixin
from flask import current_app
from hashlib import md5
from time import time
from werkzeug.security import generate_password_hash, check_password_hash

import jwt

@login.user_loader
def load_user(id):
    return Doctor.query.get(int(id))

doctors_patients = db.Table('doctors_patients',
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id')),
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'))
    )

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index = True)
    email = db.Column(db.String(128), index= True, unique = True)
    registration_number = db.Column(db.String(15), index=True, unique = True)
    password_hash = db.Column(db.String(128))
    patients = db.relationship('Patient', secondary = doctors_patients, backref = db.backref('doctor', lazy ='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_patient(self, patient):
        if not self.has_patient(patient):
            self.patients.append(patient)

    def remove_patient(self, patient):
        if self.has_patient(patient):
            self.patients.remove(patient)

    def has_patient(self, patient):
        return self.patients.filter(doctors_patients.c.patient_id == patient.id).count() > 0

    #use database queries is far more efficient than running
    #doctor.patients.all()
    def get_all_patients(self):
        return Patient.query.join(doctors_patients, (doctors_patients.c.patient_id == Patient.id)).filter(doctors_patients.c.doctor_id == self.id)

    def get_reset_password_token(self, expires_in = 600):
        return jwt.encode({'reset_password':self.id, 'exp':time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return 'Error decoding token'
        return Doctor.query.get(id)

    def __repr__(self):
        return '<Doctor {}>'.format(self.email)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(64), index = True)
    last_name = db.Column(db.String(64), index = True)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(1))
    #dob = db.column(db.DateTime)
    id_number = db.Column(db.String(13), unique=True)
    email = db.Column(db.String(128), unique = True)
    last_seen = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    doctors = db.relationship('Doctor', secondary = doctors_patients, backref = db.backref('patient', lazy = 'dynamic'), lazy = 'dynamic')

    def avatar(self, size):
        #if self.email is None:
        digest = md5('josh@gmail.com'.encode('utf-8')).hexdigest()
        #else:
        #    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def add_doctor(self, doctor):
        if not self.has_doctor(doctor):
            self.doctors.append(doctor)

    def remove_doctor(self, doctor):
        if self.has_doctor(doctor):
            self.doctors.remove(doctor)

    def has_doctor(self, doctor):
        return self.doctors.filter(doctors_patients.c.doctor_id == doctor.id).count() > 0

    #use database queries is far more efficient than running
    #doctor.patients.all()
    def get_all_doctors(self):
        return Doctor.query.join(doctors_patients, (doctors_patients.c.doctor_id == Doctor.id)).filter(doctors_patients.c.patient_id == self.id)
    def __repr__(self):
        return 'Patient {}'.format(self.name)
