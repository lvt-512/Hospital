import hashlib
import hmac

from flask import url_for
from flask_mail import Message

from my_clinic import app, mail, s
from my_clinic.models import Customer, Question, db, Patient, Time, Books, AccountPatient


def add_questions(name, email, topic, message):
    try:
        if not exist_user(email):
            customer = Customer(name=name, email=email)
            db.session.add(customer)
        else:
            customer = Customer.query.filter(Customer.email == email).first()

        question = Question(customer=customer, topic=topic, content=message)
        db.session.add(question)
        db.session.commit()

        return True
    except Exception as ex:
        print("Question Error: " + str(ex))
        return False


def add_booking(name, email, date, period):
    try:
        if not exist_user(email):
            customer = Customer(name=name, email=email)
            db.session.add(customer)
        else:
            customer = Customer.query.filter(Customer.email == email).first()

        time = Time.query.filter(Time.period == period).first()

        books = Books(booked_date=date, customer=customer, time=time)
        db.session.add(books)
        db.session.commit()

        return True
    except Exception as ex:
        print("Booking Error: " + str(ex))
        return False


def add_user(name, email, password, avatar=None):
    if not exist_user(email):
        patient = Patient(name=name, email=email, avatar=avatar)
        db.session.add(patient)
    else:
        if Customer.query.filter(Patient.email == email).first():
            patient = Customer.query.filter(Patient.email == email).first()
        else:
            pass

    password = hmac_sha256(password)
    account_patient = AccountPatient(email=patient.email, password=password, patient=patient)
    db.session.add(account_patient)

    # send the link to user via Gmail
    if email_verification(email):
        db.session.commit()
        return True

    return False


def exist_user(email):
    try:
        if Customer.query.filter(Customer.email == email).first():
            return True
        return False
    except Exception as ex:
        print(ex)


def hmac_sha256(data):
    return hmac.new(app.secret_key.encode('utf-8'),
                    data.encode('utf-8'),
                    hashlib.sha256).hexdigest()


def email_verification(email):
    try:
        token = s.dumps(email, salt='email-verification')
        link = url_for('complete_registration', token=token, _external=True)
        msg = Message('E-mail Verification',
                      recipients=[email],
                      html=f"<div>please click on the link below to complete the verification:"
                           f"<br/>{link}</div>")
        mail.send(msg)
        return True

    except Exception as ex:
        print(ex)
        return False
