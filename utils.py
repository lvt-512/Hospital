import hashlib
import hmac
import random
import string

from flask import url_for, abort
from flask_mail import Message
from sqlalchemy import text, func
from sqlalchemy.sql.functions import count

from my_clinic import app, mail, s
from my_clinic.models import Customer, Question, db, Patient, Books, AccountPatient, ClinicalRecords, Receipt, \
    ReceiptDetails, Disease, Medicine


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


def add_booking(name, email, date, time):
    try:
        if not exist_user(email):
            customer = Customer(name=name, email=email)
            db.session.add(customer)
        else:
            customer = Customer.query.filter(Customer.email == email).first()

        books = Books(booked_date=date, customer=customer, time=time)
        db.session.add(books)
        db.session.commit()

        return True
    except Exception as ex:
        print("Booking Error: " + str(ex))
        return False


def add_user(name, email, password, avatar=None, verification=True):
    if not exist_user(email):
        patient = Patient(name=name, email=email, avatar=avatar)
        db.session.add(patient)
    else:
        if Patient.query.filter(Patient.email == email).first():
            patient = Patient.query.filter(Patient.email == email).first()
        else:
            customer = Customer.query.filter(Customer.email == email).first()
            patient = customerToPatient(customer, avatar)

    password = create_password(email, password)
    account_patient = AccountPatient(email=patient.email, password=password, patient=patient)
    db.session.add(account_patient)

    # send the link to user via Gmail
    if email_verification(email):
        db.session.commit()
        return True

    return False


def customerToPatient(customer, avatar):
    customer.type = 'patient'
    db.session.add(customer)
    sql = text("INSERT INTO patient VALUES (%s, '%s')" % (customer.id, avatar))
    db.session.execute(sql)
    db.session.commit()
    patient = Patient.query.get(customer.id)
    return patient


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


def create_password(email, password=None):
    if password is None:
        # then create an account for this user
        password = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        print(password)
        # send password to user via Gmail
        try:
            msg = Message('Password for Login',
                          recipients=[email],
                          html=f"<div>This is your password: <b>{password}</b></div>")
            with app.open_resource("%s/static/images/logo.png" % app.root_path) as logo:
                msg.attach('medall.png', 'image/jpeg', logo.read())
            mail.send(msg)
        except Exception as ex:
            print(ex)
            abort(500)

    return hmac_sha256(password)


def get_amount_of_people(time, date):
    # Every period just have 2 people
    count = 0
    for book in time.books_times:
        if book.booked_date == date:
            count += 1
    return count


def get_records(patient_id):
    return ClinicalRecords.query.filter(ClinicalRecords.patient_id == patient_id).all()


def change_password(email, old_password, new_password):
    account_patient = AccountPatient.query.filter(AccountPatient.email == email).first()

    old_password = hmac_sha256(old_password)
    new_password = hmac_sha256(new_password)

    if old_password == account_patient.password:
        account_patient.password = new_password
        db.session.add(account_patient)
        db.session.commit()
        return True

    return False


def get_all_receipts():
    return db.session.query(Receipt.created_date, Customer.name,
                            func.sum(ReceiptDetails.quantity * ReceiptDetails.unit_price).label("TotalPrice")) \
        .join(Receipt, Receipt.id == ReceiptDetails.receipt_id) \
        .join(Customer, Customer.id == Receipt.patient_id).group_by(ReceiptDetails.receipt_id, Customer.name).all()


def get_profile_customer(name_patient=None):
    profile = db.session.query(Receipt.created_date, Customer.name, Customer.idCard, Customer.phone,
                               Disease.name.label("nameDis"),
                               func.sum(ReceiptDetails.quantity * ReceiptDetails.unit_price).label("TotalPrice")) \
        .join(Receipt, Receipt.id == ReceiptDetails.receipt_id) \
        .join(Customer, Customer.id == Receipt.patient_id) \
        .join(ClinicalRecords, ClinicalRecords.patient_id == Customer.id) \
        .join(Disease, Disease.id == ClinicalRecords.disease_id) \
        .group_by(ReceiptDetails.receipt_id, Customer.name)
    if name_patient:
        profile = profile.filter(Customer.name.contains(name_patient))

    return profile.all()


def get_name_receipt_detail(name_patient):
    return db.session.query(Medicine.name, ReceiptDetails.medicine_id, ReceiptDetails.quantity,
                            ReceiptDetails.unit_price, Receipt.created_date) \
        .join(Receipt, Receipt.id == ReceiptDetails.receipt_id).join(Medicine,
                                                                     Medicine.id == ReceiptDetails.medicine_id) \
        .join(Customer, Customer.id == Receipt.patient_id) \
        .filter(Customer.name == name_patient).all()


def get_stats_by_date(date_start=None, date_end=None):
    stats = db.session.query(Disease.name, count(ClinicalRecords.patient_id).label("count_di")) \
        .join(Disease, Disease.id == ClinicalRecords.disease_id)

    if date_start:
        stats = stats.filter(ClinicalRecords.checked_date.__ge__(date_start))

    if date_end:
        stats = stats.filter(ClinicalRecords.checked_date.__le__(date_end))

    return stats.group_by(ClinicalRecords.disease_id).all()
