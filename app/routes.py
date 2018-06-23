from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, AddPatientForm
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
        doc = Doctor.query.filter_by(username=form.username.data).first()
        if doc is None or not doc.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(doc, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        if not is_safe_url('next'):
            return flask.abort(400)
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
        doc = Doctor(name = form.name.data, username = form.username.data, email = form.email.data, registration_number = form.registration_number.data)
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
    page = request.args.get('page', 1, type=int)
    patients = doc.patients.paginate(page, app.config['PATIENTS_PER_PAGE'], False)
    next_url = url_for('doc', username=username, page = patients.next_num) \
        if patients.has_next else None
    prev_url = url_for('doc', username=username, page = patients.prev_num) \
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
