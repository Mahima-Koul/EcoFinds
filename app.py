from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///auction.db"
db= SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # unique user ID
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  


#-----register-----#
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # hash password before saving
        hashed_pw = generate_password_hash(password)
        
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))  # after register, go to login page

    return render_template("register.html")

#-----login-----#
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return f"Welcome {user.username}!"  # temp success message
        else:
            return "Invalid email or password"

    return render_template("login.html")



@app.route("/")
def home():
    return render_template('index.html')

if __name__=="__main__":
    with app.app_context():
        db.create_all()   # this will now create the User table
    app.run(debug=True)