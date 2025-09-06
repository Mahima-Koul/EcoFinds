from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user



app = Flask(__name__)
app.secret_key = "your_secret_key_here"  
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///auction.db"
db= SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # unique user ID
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

#---home page----
@app.route("/")
def home():
    return render_template('index.html')

#-----register-----#
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("home"))  
    return render_template("register.html")

#-----login-----#
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id      # <-- store user id
            session['username'] = user.username  # optional, for showing name
            flash("Logged in successfully!", "success")

            return redirect(url_for("home"))
        else:
            flash("Invalid email or password")

    return render_template("login.html")

#-----product adding-----#
@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    if 'user_id' not in session:
        flash("You must be logged in to add a product.", "warning")
        return redirect(url_for('login'))  # sends user to login page
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        price = float(request.form["price"])
        image = "placeholder.png"  # for now, just a placeholder

        new_product = Product(
            title=title,
            description=description,
            category=category,
            price=price,
            image=image, 
            user_id=session['user_id']
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("view_listings"))
    return render_template("add_product.html")

#-----browsing------
@app.route("/browse")
def browse():
    products = Product.query.filter_by(user_id=session['user_id']).all()
    return render_template("browse.html", products=products)


#-----product listing------
@app.route("/view-listings")
def view_listings():
    if "user_id" not in session:  # not logged in
        flash("Please log in first")
        return redirect(url_for("login"))
    products = Product.query.filter_by(user_id=session['user_id']).all()
    return render_template("view_listings.html", products=products)

#showing accounts page
@app.route("/account")
def account():
    if "user_id" not in session:  # only allow logged in users
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])  # fetch current user from DB
    return render_template("account.html", user=user)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))



if __name__=="__main__":
    with app.app_context():
        db.create_all()   # this will now create the User table
    app.run(debug=True)