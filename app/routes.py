from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, AddPatientForm, RequestPasswordResetForm, ResetPasswordForm
from app.models import Doctor, Patient
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        doc = Doctor.query.filter_by(email=form.email.data).first()
        if doc is None or not doc.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(doc, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title = 'Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        doc = Doctor(name = form.name.data, email = form.email.data, registration_number = form.registration_number.data)
        db.session.add(doc)
        doc.set_password(form.password.data)
        db.session.commit()
        flash('Congratulations, you have succesfully registered.')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/doc/<email>')
@login_required
def doc(email):
    doc = Doctor.query.filter_by(email=email).first_or_404()
    page = request.args.get('page', 1, type=int)
    patients = doc.patients.paginate(page, app.config['PATIENTS_PER_PAGE'], False)
    next_url = url_for('doc', email=email, page = patients.next_num) \
        if patients.has_next else None
    prev_url = url_for('doc', email=email, page = patients.prev_num) \
        if patients.has_prev else None
    return render_template('doc.html', doc=doc, patients = patients.items, next_url=next_url, prev_url=prev_url)

@app.route('/add_patient', methods = ['GET', 'POST'])
@login_required
def add_patient():
    form = AddPatientForm()
    if form.validate_on_submit():
        patient = Patient(name = form.name.data, age = form.age.data, email = form.email.data)
        db.session.add(patient)
        patient.add_doctor(current_user)
        db.session.commit()
        flash('Patient succesfully added.')
        return redirect(url_for('add_patient'))
    return render_template('add_patient.html', title = 'Add Patient', form=form)

@app.route('/request_password_reset', methods = ['GET', 'POST'])
def request_password_reset():
    if (current_user.is_authenticated):
        return redirect(url_for('index'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit:
        doc = Doctor.query.filter_by(email=form.email.data).first()
        if doc:
            send_password_reset_email(doc)
        flash('Check email')
        #return redirect(url_for('login'))
    return render_template('request_password_reset.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    doc = Doctor.verify_reset_password_token(token)
    if not doc:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        doc.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form = form)
