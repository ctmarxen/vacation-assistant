from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired

class HomeForm(FlaskForm):
    register = SubmitField("Register")
    login = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password1 = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    secret_key = PasswordField("Secret Key (Type '123')", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")

class LocationForm(FlaskForm):
    location = StringField("Choose your location (e.g. New York City, 10001).", validators=[DataRequired()])
    radius = IntegerField("Enter a number for how many miles you would travel from the location (e.g. 5).", validators=[DataRequired()])
    number_of_results = IntegerField("Enter a number for the results per category (e.g. 10).", validators=[DataRequired()])
    submit = SubmitField("Update Location")



