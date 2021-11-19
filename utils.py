import hashlib
import hmac
import json

from flask import url_for
from flask_mail import Message

from my_clinic import app, mail, s
from my_clinic.models import Customer, Question, db, Patient, Time, Books, AccountPatient


def add_questions(questions):
    if questions:
        try:
            if not exist_user(questions["email"]):
                customer = Customer(name=questions["name"], email=questions["email"])
                db.session.add(customer)
            else:
                customer = Customer.query.filter(Customer.email == questions["email"]).first()

            question = Question(customer=customer, topic=questions["topic"], content=questions["message"])
            db.session.add(question)
            db.session.commit()

            return True
        except Exception as ex:
            print("Question Error: " + str(ex))

    return False


def add_booking(books):
    if books:
        try:
            if not exist_user(books["email"]):
                customer = Customer(name=books["name"], email=books["email"])
                db.session.add(customer)
            else:
                customer = Customer.query.filter(Customer.email == books["email"]).first()
            time = Time.query.filter(Time.period == books["period"]).first()

            books = Books(customer, time)
            db.session.add(books)
            db.session.commit()

            return True
        except Exception as ex:
            print("Booking Error: " + str(ex))

    return False


def add_user(name, email, password, avatar=None):
    patient = Patient(name=name, email=email, avatar=avatar)
    db.session.add(patient)

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
        if Customer.query.filter(Patient.email == email).first():
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
