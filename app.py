import hashlib

from flask_login import login_user, logout_user

from my_clinic import app, my_login
from flask import render_template, request, redirect

from my_clinic.models import AccountPatient, AccountAssistant, Account


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
    password = str(hashlib.md5(password.encode("utf-8")).digest())

    user = Account.query.filter(AccountAssistant.username == username,
                                AccountAssistant.password == password).first()
    if user:  # login success
        login_user(user)

    # redirect: from admin
    return redirect("/admin")  # redirect: change the page


# User Login
@app.route("/user-login", methods=['get', 'post'])
def user_login_exe():
    err_msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        password = str(hashlib.md5(password.encode("utf-8")).digest())

        user = Account.query.filter(AccountPatient.username == username,
                                    AccountPatient.password == password).first()

        if user:
            login_user(user)
            return redirect(request.args.get("next", "/"))
        else:
            err_msg = "Incorrect username or password!"

    return render_template("login-user.html",
                           err_msg=err_msg,
                           log=request.args.get("log"))  # get into form register


# Log out
@app.route("/user-logout")
def user_logout_exe():
    logout_user()

    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
