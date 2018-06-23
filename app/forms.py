from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange
from app.models import Doctor, Patient

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=None)
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    registration_number = StringField('Registration number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        doc = Doctor.query.filter_by(username=username.data).first()
        if doc is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        doc = Doctor.query.filter_by(email=email.data).first()
        if doc is not None:
            raise ValidationError('Please use a different email address.')

class AddPatientForm(FlaskForm):
    name = StringField('Patient Name', validators=[DataRequired()])
    age = IntegerField('Age', validators = [NumberRange(0, 120, 'Invalid age')])
    email = StringField('Email')
    submit = SubmitField('Add')
