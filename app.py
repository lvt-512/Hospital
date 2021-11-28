import datetime
import hashlib
import hmac
import json

import requests
from itsdangerous import SignatureExpired

import utils
from flask_login import login_user, logout_user, current_user

from my_clinic import app, my_login, client \
    , GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, db, s, BOOKING_MAX
from flask import render_template, request, redirect, jsonify

from my_clinic.models import AccountPatient, AccountAssistant, Account, Patient, Customer, Time


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/about')
def about_us():
    return render_template('about-us.html')


@app.route('/schedule')
def schedule():
    return render_template('schedule.html', booking_max=BOOKING_MAX)


@app.route('/question')
def question():
    return render_template('question.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/blog/post')
def blog_post():
    return render_template('blog-single.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/user-profile')
def user_profile():
    return render_template("user_profile.html", records=utils.get_records(current_user.patient.id))


@my_login.user_loader
def user_loader(account_id):
    return AccountPatient.query.get(account_id) if AccountPatient.query.get(account_id) \
        else AccountAssistant.query.get(account_id)


# Admin Login
@app.route("/admin-login", methods=["post"])
def admin_login_exe():
    username = request.form.get("username")
    password = request.form.get("password")
    # password encryption
    password = hmac.new(app.secret_key.encode('utf-8'),
                        password.encode('utf-8'),
                        hashlib.sha256).hexdigest()

    user = Account.query.filter(AccountAssistant.username == username,
                                AccountAssistant.password == password).first()
    if user:  # login success
        login_user(user)

    # redirect: from admin
    return redirect("/admin")  # redirect: change the page


# User Login
@app.route("/user-login", methods=['get', 'post'])
def user_login_exe():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        password = utils.hmac_sha256(password)

        user = Account.query.filter(AccountPatient.email == email,
                                    AccountPatient.password == password).first()

        if user:
            if user.active:
                login_user(user)
                return jsonify({"redirect": request.args.get("next", "/")}), 200
            else:
                if utils.email_verification(email):
                    return jsonify({"message": "You have to be ACTIVE for your email!"}), 406  # Not Acceptable

                return jsonify({"message": "The system has some errors!. PLease try later"})

        return jsonify({"message": "Incorrect username or password!"}), 401  # Unauthorized
    else:
        return render_template("login-user.html")


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/user-login/google")
def loginWithGoogle():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/user-login/google/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    if AccountPatient.query.filter(AccountPatient.email == users_email).first():
        account_patient = AccountPatient.query.filter(AccountPatient.email == users_email).first()
    else:
        # Doesn't exist? Add it to the database.
        if not utils.exist_user(users_email):
            # Create a user in your db with the information provided by Google
            patient = Patient(name=users_name, email=users_email, avatar=picture)
            db.session.add(patient)
        else:
            if Patient.query.filter(Patient.email == users_email).first():
                patient = Patient.query.filter(Patient.email == users_email).first()
            else:
                customer = Customer.query.filter(Customer.email == users_email).first()
                patient = utils.customerToPatient(customer, avatar=picture)

        password = utils.create_password(users_email)
        account_patient = AccountPatient(active=True, email=patient.email, password=password, patient=patient)
        db.session.add(account_patient)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(account_patient)

    # Send user back to homepage
    return redirect("/")


# Log out
@app.route("/user-logout")
def user_logout_exe():
    logout_user()

    return redirect("/")


@app.route("/api/validate-email", methods=["post"])
def validate_email():
    email = request.values["registerEmail"]
    user_email = Account.query.filter(Account.email == email).first()
    if user_email:
        return jsonify(False)
    return jsonify(True)


@app.route("/api/change-password", methods=["post"])
def change_password():
    old = request.form.get("old_password")
    new = request.form.get("new_password")

    if utils.change_password(current_user.patient.account.email, old, new):
        return jsonify({"message": "Change Successful!"}), 200

    return jsonify({"message": "ERROR: Incorrect password!"}), 405


@app.route("/api/check-booking-date", methods=["post"])
def check_booking_date():
    date = request.form.get("bookingdate")
    if datetime.datetime.strptime(date, '%d/%m/%Y') > datetime.datetime.now():
        return jsonify(True)
    return jsonify(False)


@app.route("/api/check-booking-time", methods=["post"])
def check_booking_time():
    time = request.form.get("bookingtime")
    time = datetime.datetime.strptime(time, '%I:%M %p').time()
    if time < datetime.time(8, 0, 0) or time > datetime.time(19, 0, 0) \
            or datetime.time(13, 0, 0) > time > datetime.time(12, 0, 0):
        return jsonify(False)
    return jsonify(True)


@app.route("/user-register", methods=['post'])
def user_register():
    data = {
        "name": request.form.get("registerName"),
        "email": request.form.get("registerEmail"),
        "password": request.form.get("registerPassword"),
        # default avatar
        "avatar": "https://res.cloudinary.com/dtsahwrtk/image/upload/v1635424275/samples/people/smiling-man.jpg"
    }

    if utils.add_user(**data):
        return jsonify({"message": "Create Account successful!!!"}), 200  # OK
    else:
        return jsonify({"message": "Data has some problems! Maybe."}), 404


@app.route("/user-register/complete")
def complete_registration():
    try:
        token = request.args.get("token")
        email = s.loads(token, salt="email-verification", max_age=60)  # max_age: milliseconds
        user = Account.query.filter(AccountPatient.email == email).first()
        user.active = True
        db.session.add(user)
        db.session.commit()
        return "<h1>Your Email has been verified</h1>"
    except SignatureExpired:
        return "<h1>The token is expired</h1>"


@app.route("/api/add-questions", methods=["post"])
def add_questions():
    questions = {
        "name": request.form.get("name", current_user.patient.name if current_user.is_authenticated else ""),
        "email": request.form.get("email", current_user.patient.email if current_user.is_authenticated else ""),
        "topic": request.form.get("topic"),
        "message": request.form.get("message")
    }
    if utils.add_questions(**questions):
        return jsonify({"message": "add questions success!"}), 200

    return jsonify({"message": "can't add questions!"}), 404


@app.route("/api/add-booking", methods=["post"])
def add_booking():
    books = {
        "name": request.form.get("bookingname", current_user.patient.name if current_user.is_authenticated else ""),
        "email": request.form.get("bookingemail", current_user.patient.name if current_user.is_authenticated else ""),
        "date": request.form.get("bookingdate")
    }

    books["date"] = datetime.datetime.strptime(books["date"], '%d/%m/%Y')

    period = datetime.datetime.strptime(request.form.get("bookingtime"), '%I:%M %p').hour
    period = f"{period:02d}:00 - {period + 1:02d}:00"
    time = Time.query.filter(Time.period == period).first()

    if utils.get_amount_of_people(time, books["date"]) == BOOKING_MAX:
        return jsonify({"message": "Maximum of people!"}), 400

    books["time"] = time

    if utils.add_booking(**books):
        return jsonify({
            "message": "booking successfully!",
            "amount": utils.get_amount_of_people(time, books["date"])
        }), 200

    return jsonify({"message": "can't add booking!"}), 404


@app.route("/api/load-schedule")
def load_schedule():
    try:
        time = int(request.args.get('bookingtime'))
        period = f"{time:02d}:00 - {time + 1:02d}:00"
        time = Time.query.filter(Time.period == period).first()

        date = request.args.get('bookingdate')
        date = datetime.datetime.strptime(date, '%d/%m/%Y')

        amount = utils.get_amount_of_people(time, date)

        return jsonify({"amount": amount}), 200
    except Exception as ex:
        print(ex)
        return jsonify({"message": "Error"}), 404


if __name__ == '__main__':
    app.run(debug=True)
