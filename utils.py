import hashlib
import hmac

from my_clinic import app
from my_clinic.models import Customer, Question, db, Patient


def add_questions(questions):
    if questions:
        try:
            customer = Customer(name=questions["name"], email=questions["email"])
            db.session.add(customer)
            db.session.commit()

            question = Question(customer=customer, topic=questions["topic"], content=questions["message"])
            db.session.add(question)
            db.session.commit()

            return True
        except Exception as ex:
            print("RECEIPT ERROR: " + str(ex))

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