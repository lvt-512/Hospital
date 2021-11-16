import hashlib
import hmac

from my_clinic import app
from my_clinic.models import Customer, Question, db, Patient, Time, Books


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
