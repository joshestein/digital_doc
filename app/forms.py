from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange
from app.models import Doctor, Patient

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    registration_number = StringField('Registration Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        doc = Doctor.query.filter_by(email=email.data).first()
        if doc is not None:
            raise ValidationError('Please use a different email address.')

class AddPatientForm(FlaskForm):
    name = StringField('Patient Name', validators=[DataRequired()])
    age = IntegerField('Age', validators = [NumberRange(0, 120, 'Invalid age')])
    email = StringField('Email')
    submit = SubmitField('Add')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request password reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class EmailPatientForm(FlaskForm):
    subject = StringField('Subject')
    body = StringField('Body')
    submit = SubmitField('Send')
