from my_clinic.models import Customer, Question, db


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

def add_times():
    pass