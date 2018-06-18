from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddPatientForm
from app.models import Doctor, Patient
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    patients = [
        {
            'name':'Josh',
            'age':22
        },
        {
            'name':'Kristien',
            'age':20
        }
    ]
    return render_template('index.html', title='Home', patients=patients)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        doc = Doctor.query.filter_by(username=form.username.data).first()
        if doc is None or not doc.check_password(form.password.data):
            flash('Invalid username or password')
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
        doc = Doctor(username = form.username.data, email = form.email.data)
        doc.set_password(form.password.data)
        db.session.add(doc)
        db.session.commit()
        flash('Congratulations, you have succesfully registered.')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/doc/<username>')
@login_required
def doc(username):
    doc = Doctor.query.filter_by(username=username).first_or_404()
    patients = doc.patients.all()
    return render_template('doc.html', doc=doc, patients = patients)

@app.route('/add_patient', methods = ['GET', 'POST'])
@login_required
def add_patient():
    form = AddPatientForm()
    if form.validate_on_submit():
        patient = Patient(doctor = current_user, name = form.name.data, age = form.age.data, email = form.email.data)
        db.session.add(patient)
        db.session.commit()
        flash('Patient succesfully added.')
        return redirect(url_for('add_patient'))
    return render_template('add_patient.html', title = 'Add Patient', form=form)
