from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "your_secret_key_here"  
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

        return redirect(url_for("home"))  # after register, go to home page

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
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)  # placeholder for image URL or filename
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # optional: which user posted it


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
            title=title, description=description, category=category, price=price, image=image, user_id=session['user_id']
        )
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for("browse"))

    return render_template("add_product.html")


@app.route("/browse")
def browse():
    category_filter = request.args.get("category")
    search_query = request.args.get("q")

    products = Product.query

    if category_filter:
        products = products.filter_by(category=category_filter)
    if search_query:
        products = products.filter(Product.title.contains(search_query))

    products = products.all()
    return render_template("browse.html", products=products)


@app.route("/show_users")
def show_users():
    users = User.query.all()
    output = "<h2>Registered Users:</h2>"
    for u in users:
        output += f"<p>ID: {u.id} | Username: {u.username} | Email: {u.email} | Password: {u.password}</p>"
    return output



@app.route("/")
def home():
    return render_template('index.html')

if __name__=="__main__":
    with app.app_context():
        db.create_all()   # this will now create the User table
    app.run(debug=True)