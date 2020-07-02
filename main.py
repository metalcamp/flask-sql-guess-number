import hashlib
import random
import uuid

from flask import Flask, render_template, request, make_response, redirect, url_for
from model import User, db

app = Flask(__name__)
db.create_all()

@app.route("/", methods=["GET"])
def index():
    # email_address = request.cookies.get("email")
    session_token = request.cookies.get("session_token")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    #create secret number
    secret_number = random.randint(1,30)

    #check if user exists
    user = db.query(User).filter_by(email=email).first()

    if not user:
        # create user object
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password)

        # save to db
        db.add(user)
        db.commit()

    # check if password is incorrect
    if hashed_password != user.password:
        return "WRONG PASSWORD. Please try again."
    elif hashed_password == user.password:
        # create a random token
        session_token = str(uuid.uuid4())
        user.session_token = session_token
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for("index")))
        # response.set_cookie("email", email)
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response

@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))
    # email_address = request.cookies.get("email")
    session_token = request.cookies.get("session_token")

    # get user from db
    user = db.query(User).filter_by(session_token=session_token).first()

    if guess == user.secret_number:
        message = "Correct"
        new_secret = random.randint(1,30)

        user.secret_number = new_secret

        db.add(user)
        db.commit()
    elif guess > user.secret_number:
        message = "Your guess is not correct, try something smaller"
    elif guess < user.secret_number:
        message = "Your guess is not correct, try something bigger"

    return render_template("result.html", message=message)

@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    #get user from db based on his email address / session token
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))

@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")

        user.name = name
        user.email = email

        db.add(user)
        db.commit()
        return redirect(url_for("profile"))

@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        db.delete(user)
        db.commit()
        return redirect(url_for("index"))

@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).all()

    return render_template("users.html", users=users)

@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))

    return render_template("user_details.html", user=user)

if __name__ == '__main__':
    app.run()
