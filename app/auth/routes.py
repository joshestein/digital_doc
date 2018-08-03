from flask import render_template, flash, redirect, request, url_for, current_app
from app import db
from app.auth import bp
from app.auth.forms import *
from app.auth.email import send_password_reset_email, send_email
from app.models import Doctor, Patient
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

@bp.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        doc = Doctor.query.filter_by(email=form.email.data).first()
        if doc is None or not doc.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(doc, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title = 'Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/all_patients/<email>')
def all_patients(email):
    doc = Doctor.query.filter_by(email=email).first_or_404()
    page = request.args.get('page', 1, type=int)
    patients = doc.patients.paginate(page, current_app.config['PATIENTS_PER_PAGE'], False)
    next_url = url_for('auth.all_patients', email=email, page = patients.next_num) \
        if patients.has_next else None
    prev_url = url_for('auth.all_patients', email=email, page = patients.prev_num) \
        if patients.has_prev else None
    return render_template('auth/all_patients.html', doc=doc, patients = patients.items, next_url=next_url, prev_url=prev_url)


@bp.route('/add_patient', methods = ['GET', 'POST'])
def add_patient():
    form = AddPatientForm()
    if form.validate_on_submit():
        try:
            patient = Patient(first_name = form.first_name.data, last_name = form.last_name.data, age = form.age.data, sex=form.sex.data, email = form.email.data)
            db.session.add(patient)
            patient.add_doctor(current_user)
            db.session.commit()
            flash('Patient succesfully added.')
        except Exception as e:
            flash('Failed to add patient. '+str(e))
        return redirect(url_for('auth.add_patient'))
    return render_template('auth/add_patient.html', title = 'Add Patient', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            doc = Doctor(name = form.name.data, email = form.email.data, registration_number = form.registration_number.data)
            db.session.add(doc)
            doc.set_password(form.password.data)
            db.session.commit()
            flash('Congratulations, you have succesfully registered.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Error registering: '+str(e))
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', title = 'Register', form=form)


@bp.route('/request_password_reset', methods = ['GET', 'POST'])
def request_password_reset():
    if (current_user.is_authenticated):
        return redirect(url_for('main.index'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        doc = Doctor.query.filter_by(email=form.email.data).first()
        if doc:
            send_password_reset_email(doc)
        flash('Check email')
        return redirect(url_for('auth.login'))
    return render_template('auth/request_password_reset.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    doc = Doctor.verify_reset_password_token(token)
    if not doc:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        doc.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form = form)


@bp.route('/email_patient/<email>', methods=['GET', 'POST'])
def email_patient(email):
    form = EmailPatientForm();
    if form.validate_on_submit():
        #subject, sender, reciever, text_body, html_body
        send_email(form.subject.data, current_user.email, email, form.body.data, form.body.data)
        flash('Your email has succesfully been sent.')
        return redirect(url_for('auth.all_patients', email=current_user.email))
    return render_template('auth/email_patient.html', email=email, form=form)


@bp.route('/patient_info/<patient_id>')
def patient_info(patient_id):
    patient = Patient.query.filter_by(id=patient_id).first()
    return render_template('auth/patient_info.html', patient=patient)
