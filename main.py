from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from forms import LoginForm, RegisterForm, HomeForm, LocationForm

app = Flask(__name__)
Bootstrap(app)

if os.environ.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
else:
    load_dotenv()
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URLL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///vacation.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    restaurants = relationship("Restaurant", back_populates="patron")
    bars = relationship("Bar", back_populates="patron")
    coffee_shops = relationship("CoffeeShop", back_populates="patron")
    activities = relationship("Activity", back_populates="patron")


class Restaurant(db.Model):
    __tablename__ = "restaurants"
    id = db.Column(db.Integer, primary_key=True)
    patron_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    patron = relationship("User", back_populates="restaurants")
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.String(10), nullable=True)


class Bar(db.Model):
    __tablename__ = "bars"
    id = db.Column(db.Integer, primary_key=True)
    patron_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    patron = relationship("User", back_populates="bars")
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.String(10), nullable=True)


class CoffeeShop(db.Model):
    __tablename__ = "coffee_shops"
    id = db.Column(db.Integer, primary_key=True)
    patron_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    patron = relationship("User", back_populates="coffee_shops")
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.String(10), nullable=True)

class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    patron_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    patron = relationship("User", back_populates="activities")
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)


db.create_all()

API_KEY = os.environ.get("API_KEY")
YELP_ENDPOINT = "https://api.yelp.com/v3/businesses/search"
headers = {
    "Authorization": f"Bearer {API_KEY}"
}


def change_location(location, radius, number_of_results):
    params = {
        'location': location,
        # Yelp uses meters rather than miles for measuring distance
        'radius': radius * 1610,
        'limit': number_of_results,
        'sort_by': 'rating',
        'term': 'restaurants'
    }

    # Update Restaurant table
    restaurant_data = requests.get(url=YELP_ENDPOINT, params=params, headers=headers).json()['businesses']
    for restaurant in restaurant_data:
        try:
            new_restaurant = Restaurant(
                patron=current_user,
                name=restaurant['name'],
                image_url=restaurant['image_url'],
                url=restaurant['url'],
                rating=restaurant['rating'],
                price=restaurant['price'],
            )
        except KeyError:
            new_restaurant = Restaurant(
                patron=current_user,
                name=restaurant['name'],
                image_url=restaurant['image_url'],
                url=restaurant['url'],
                rating=restaurant['rating']
            )
        finally:
            db.session.add(new_restaurant)

    # Update Drinks table
    params['term'] = 'drinks'
    bar_data = requests.get(url=YELP_ENDPOINT, params=params, headers=headers).json()['businesses']
    for bar in bar_data:
        try:
            new_bar = Bar(
                patron=current_user,
                name=bar['name'],
                image_url=bar['image_url'],
                url=bar['url'],
                rating=bar['rating'],
                price=bar['price'],
            )
        except KeyError:
            new_bar = Bar(
                patron=current_user,
                name=bar['name'],
                image_url=bar['image_url'],
                url=bar['url'],
                rating=bar['rating'],
            )
        finally:
            db.session.add(new_bar)

    # Update Coffee table
    params['term'] = 'coffee'
    coffee_data = requests.get(url=YELP_ENDPOINT, params=params, headers=headers).json()['businesses']
    for coffee_shop in coffee_data:
        try:
            new_coffee_shop = CoffeeShop(
                patron=current_user,
                name=coffee_shop['name'],
                image_url=coffee_shop['image_url'],
                url=coffee_shop['url'],
                rating=coffee_shop['rating'],
                price=coffee_shop['price'],
            )
        except KeyError:
            new_coffee_shop = CoffeeShop(
                patron=current_user,
                name=coffee_shop['name'],
                image_url=coffee_shop['image_url'],
                url=coffee_shop['url'],
                rating=coffee_shop['rating']
            )
        finally:
            db.session.add(new_coffee_shop)

    # Update activities table
    params['term'] = 'active life'
    activity_data = requests.get(url=YELP_ENDPOINT, params=params, headers=headers).json()['businesses']
    for activity in activity_data:
        new_activity = Activity(
            patron=current_user,
            name=activity['name'],
            image_url=activity['image_url'],
            url=activity['url'],
            rating=activity['rating'],
        )
    db.session.add(new_activity)
    db.session.commit()

# To keep the copyright year in the footer updated
year = datetime.now().year

@app.route("/", methods=["GET", "POST"])
def home():
    form = HomeForm()
    if form.validate_on_submit():
        if form.register.data:
            return redirect(url_for("register"))
        elif form.login.data:
            return redirect(url_for("login"))
    return render_template("login.html", form=form, year=year)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password1 = form.password1.data
        password2 = form.password2.data
        secret_key = form.secret_key.data
        if User.query.filter_by(email=email).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        elif secret_key != os.environ.get("SECRET"):
            flash("To successfully register, you must submit the correct secret key. Please register again.")
            return redirect(url_for("register"))
        elif password1 != password2:
            flash("To successfully register, your passwords must match. Please register again.")
            return redirect(url_for("register"))
        else:
            hash_and_salted_password = generate_password_hash(
                password1,
                method='pbkdf2:sha256',
                salt_length=10
            )
            new_user = User(
                email=email,
                password=hash_and_salted_password
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("restaurants", registered=True))
    return render_template("login.html", form=form, year=year)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Before logging in, you must register first.")
            return redirect(url_for('register'))
        elif not check_password_hash(user.password, password):
            flash("To successfully log in, you must submit the correct password. Please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            if len(user.restaurants) == 0:
                return redirect(url_for("update_location"))
            else:
                return redirect(url_for("restaurants"))
    return render_template("login.html", form=form, year=year)




@app.route("/update-location", methods=["GET", "POST"])
@login_required
def update_location():
    form = LocationForm()
    if form.validate_on_submit():
        # Updating the three tables by first deleting the old data
        Restaurant.query.filter_by(patron=current_user).delete()
        Bar.query.filter_by(patron=current_user).delete()
        CoffeeShop.query.filter_by(patron=current_user).delete()
        Activity.query.filter_by(patron=current_user).delete()

        # Updating the three tables by adding the new data
        new_location = form.location.data
        new_radius = int(form.radius.data)
        new_number_of_results = int(form.number_of_results.data)
        change_location(location=new_location, radius=new_radius, number_of_results=new_number_of_results)
        return redirect(url_for("restaurants"))
    return render_template("venue.html", form=form, title="Location", year=year)


@app.route("/restaurants")
@login_required
def restaurants():
    if len(current_user.restaurants) == 0:
        return redirect(url_for("update_location"))
    return render_template("venue.html", title="Restaurants", year=year, venues=current_user.restaurants)


@app.route("/drinks")
@login_required
def drinks():
    if len(current_user.bars) == 0:
        return redirect(url_for("update_location"))
    return render_template("venue.html", title="Drinks", year=year, venues=current_user.bars)


@app.route("/coffee")
@login_required
def coffee():
    if len(current_user.coffee_shops) == 0:
        return redirect(url_for("update_location"))
    return render_template("venue.html", title="Coffee", year=year, venues=current_user.coffee_shops)

@app.route("/activities")
@login_required
def activities():
    if len(current_user.activities) == 0:
        return redirect(url_for("update_location"))
    return render_template("venue.html", title="Activities", year=year, venues=current_user.activities)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
