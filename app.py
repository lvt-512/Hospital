import hashlib
import hmac
import json
import random
import string

import requests

import utils
from flask_login import login_user, logout_user

from my_clinic import app, my_login, client, GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, db
from flask import render_template, request, redirect, jsonify

from my_clinic.models import AccountPatient, AccountAssistant, Account, Patient


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/about')
def about_us():
    return render_template('about-us.html')


@app.route('/schedule')
def schedule():
    return render_template('schedule.html')


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
            login_user(user)
            return jsonify({"redirect": request.args.get("next", "/")}), 200

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

    # Check if email exist
    account_patient = AccountPatient.query.filter(AccountPatient.email == users_email).first()

    # Doesn't exist? Add it to the database.
    if not utils.exist_user(users_email):
        # Create a user in your db with the information provided by Google
        patient = Patient(name=users_name, email=users_email, avatar=picture)
        db.session.add(patient)

        # then create an account for this user
        password = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        print(password)
        password = utils.hmac_sha256(password)
        account_patient = AccountPatient(email=patient.email, password=password, patient=patient)
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


@app.route("/api/add-questions", methods=["post"])
def add_questions_exe():
    questions = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "topic": request.form.get("topic"),
        "message": request.form.get("message"),
    }
    if utils.add_questions(questions):
        return jsonify({"message": "add questions success!"}), 200

    return jsonify({"message": "can't add questions!"}), 404


if __name__ == '__main__':
    app.run(debug=True)
