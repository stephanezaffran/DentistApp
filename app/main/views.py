import sys
from datetime import date

import requests
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from markupsafe import Markup
from app.auth.views import login_and_referer_required
from app.main import main_blueprint
from app.forms import AppointmentForm, PatientForm, LoginForm
from app.models import Appointment, Patient, db
from app.services import event_services
from wtforms.validators import DataRequired, Optional
from wtforms import StringField, PasswordField, DateField, TimeField, SelectField
from sqlalchemy import delete, update, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from whatsapp_api_client_python import API
from googleapiclient.errors import HttpError

unsaved_appointments = []  # List to store unsaved appointments


@main_blueprint.route('/')
@login_and_referer_required
def home():
    return render_template('/home.html')


@main_blueprint.route('/change_google_account')
@login_and_referer_required
def change_google_account():
    event_services.change_google_account()
    return redirect(url_for('auth.logout'))


@main_blueprint.route('/dashboard')
@login_and_referer_required
def dashboard():
    today = date.today()
    print(f'today: {today}')
    appointments = Appointment.query.filter_by(user=current_user).filter(func.date(Appointment.date) >= today).order_by(Appointment.date).all()
    return render_template('dashboard.html', appointments=appointments)


@main_blueprint.route('/patient_list')
@login_and_referer_required
def patient_list():
    patients = Patient.query.order_by(Patient.surname).all()
    return render_template('patient_list.html', patients=patients)


@main_blueprint.route('/add_appointment', methods=['GET', 'POST'])
@login_and_referer_required
def add_appointment():
    form = AppointmentForm()
    form.patient.choices = [(patient.id, patient.surname + '   ' + patient.name + '    ' + patient.identity_number)
                            for patient in Patient.query.order_by(Patient.surname).all()] + [(0, 'add new user')]
    # print(form.patient.choices)

    if form.patient.data == 0:
        date = DateField('Date', validators=[Optional()])
        start_time = TimeField('Time', validators=[Optional()])
        end_time = TimeField('Time', validators=[Optional()])
        form = PatientForm()
        return render_template('add_patient.html', form=form)
    else:
        date = DateField('Date', validators=[DataRequired()])
        start_time = TimeField('Time', validators=[DataRequired()])
        end_time = TimeField('Time', validators=[DataRequired()])

    if form.validate_on_submit():
        date = form.date.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        patient_id = form.patient.data
        message = form.message.data
        patient_name = ""
        for value, label in form.patient.choices:
            if value == patient_id:
                patient_name = label
        try:
            patient = Patient.query.get(patient_id)
            #user = User.query.filter_by(username=username).first()

            event_id = event_services.create_new_event(name=patient.name, surname=patient.surname,
                                                       phone_number=patient.phone_number,
                                                       email=patient.email, message=message,
                                                       identity_number=patient.identity_number,
                                                       date=date, start_time=start_time, end_time=end_time)


            appointment = Appointment(patient_name=patient_name, date=date, start_time=start_time, end_time=end_time,
                                      user_id=current_user.id, patient_id=patient_id, message=message, calendar_id=event_id)


            db.session.add(appointment)
            db.session.commit()

            flash('Appointment added successfully.', 'success')
            print(f"patient_name: {patient.name} ")

        except IntegrityError as e:
            db.session.rollback()
            flash(f'integrity error adding Appointment.  {e}', 'error')
            return redirect(url_for('main.dashboard'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'SQLAlchemy error adding Appointment.  {e}', 'error')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            flash(f'error integrity data, please check your fields   {e}', 'error')
            return render_template('add_appointment.html', form=form)

        return redirect(url_for('main.dashboard'))

    return render_template('add_appointment.html', form=form)


@main_blueprint.route('/update_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_and_referer_required
def update_appointment(appointment_id):

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        form = AppointmentForm(obj=appointment)

        form.patient.choices = [(patient.id, patient.surname + '   ' + patient.name + '    ' + patient.identity_number)
                                for patient in Patient.query.all()] + [(0, 'add new user')]
        # form.patient.default = appointment.patient_id
        form.patient.render_kw = {'disabled': True}

        form.patient.data = appointment.patient_id
        # form.date.data = appointment.date
        # form.start_time.data = appointment.start_time
        # form.end_time.data = appointment.end_time
        # form.message.data = appointment.message

        if form.validate_on_submit():
            print(f"entered to orm.validate_on_submit date: {form.date.data}")
            appointment.date = form.date.data
            appointment.start_time = form.start_time.data
            appointment.end_time = form.end_time.data
            appointment.patient_id = form.patient.data
            appointment.message = form.message.data

            # for value, label in form.patient.choices:
            #     if value == appointment.patient_id:
            #         appointment.patient_name = label

            db.session.add(appointment)
            db.session.commit()
            event_services.update_event(message=appointment.message,date=appointment.date, start_time=appointment.start_time,
                                        end_time=appointment.end_time, calendar_id=appointment.calendar_id)
            flash('appointment updated successfully.', 'success')
            return redirect(url_for('main.dashboard'))

        else:

            print('Form validation failed: {}'.format(form.errors), 'error')
            print(f"form.date.data {form.date.data} form.start_time.data {form.start_time.data} form.patient.data {form.patient.data}")
            print("not validate_on_submit")

        return render_template('update_appointment.html', form=form, appointment=appointment)

    except IntegrityError as e:
        db.session.rollback()
        flash(f'integrity error updating Appointment.  {e}', 'error')
        return redirect(url_for('main.dashboard'))

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'SQLAlchemy error updating Appointment.  {e}', 'error')
        return redirect(url_for('main.dashboard'))



@main_blueprint.route('/delete_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_and_referer_required
def delete_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()

        event_services.delete_event(appointment.calendar_id)

        return redirect(url_for('main.dashboard'))

    except IntegrityError as e:
        db.session.rollback(appointment_id)
        flash(f'integrity error delete Appointment.  {e}', 'error')
        return redirect(url_for('main.dashboard'))

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'SQLAlchemy error delete Appointment.  {e}', 'error')
        return redirect(url_for('main.dashboard'))


@main_blueprint.route('/add_patient', methods=['GET', 'POST'])
@login_and_referer_required
def add_patient():
    form = PatientForm()

    if form.validate_on_submit():

        name = form.name.data
        surname = form.surname.data
        phone_number = form.phone_number.data
        email = form.email.data
        identity_number = form.identity_number.data if form.identity_number.data else '0'

        patient = Patient(name=name, surname=surname, phone_number=phone_number, email=email, identity_number=identity_number)

        try:
            db.session.add(patient)
            db.session.commit()

            flash('Patient added successfully.', 'success')
            print(f"patient_name: {patient.name} ", file=sys.stdout)
            return redirect(url_for('main.patient_list'))

        except IntegrityError as e:
            db.session.rollback()
            flash(f'integrity error adding  patient.  {e}', 'error')
            return redirect(url_for('main.add_patient'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'SQLAlchemy error adding  patient.  {e}', 'error')
            return redirect(url_for('main.add_patient'))

    return render_template('add_patient.html', form=form)


@main_blueprint.route('/update_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_and_referer_required
def update_patient(patient_id):

    try:
        patient = Patient.query.get_or_404(patient_id)
        form = PatientForm(obj=patient)

        try:
            if form.validate_on_submit():
                form.populate_obj(patient)
                db.session.commit()

                flash('Patient updated successfully.', 'success')
                print(f"patient_name: {patient.name} ", file=sys.stdout)
                return redirect(url_for('main.patient_list'))

        except IntegrityError as e:
            db.session.rollback()
            flash(f'integrity error adding  patient.  {e}', 'error')
            return redirect(url_for('main.update_patient'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'SQLAlchemy error adding  patient.  {e}', 'error')
            return render_template('update_patient.html', form=form, patient=patient)

    except SQLAlchemyError as e:
        flash(f'SQLAlchemy error getting selected patient.  {e}', 'error')
        return render_template('patient_list.html', form=form, patient=patient)

    return render_template('update_patient.html', form=form, patient=patient)


@main_blueprint.route('/delete_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_and_referer_required
def delete_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        Appointment.query.filter_by(patient_id=patient.id).delete()

        db.session.delete(patient)
        db.session.commit()
        return redirect(url_for('main.patient_list'))

    except IntegrityError as e:
        db.session.rollback()
        flash(f'SQLAlchemy error delleting selected patient.  {e}', 'error')
        # Handle the error, e.g., show an error message or redirect to an error page
        return redirect(url_for('main.patient_list'))
