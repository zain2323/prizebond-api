from api.models import User, Prize
from wtforms.fields import SelectField, IntegerField, DateField
from wtforms.fields.simple import PasswordField, SubmitField
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields import BooleanField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import (DataRequired, EqualTo, Length, Email,
                                ValidationError)
from wtforms.fields import TextAreaField
from api.webadmin.utils import normalize_serials

# Validator that checks every field is free from slash (/) because this may
# cause error in some cases.


def check_slash(form, field):
    if "/" in field.data:
        raise ValidationError("/ is not allowed.")


class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(
        message="Name field can not be empty!"),
        Length(min=3, max=30), check_slash])
    email = StringField('Email', validators=[DataRequired(
        message="Email field can not be empty!"),
        Length(min=5, max=30), Email(), check_slash])
    password = PasswordField("Password", validators=[DataRequired(
        message="Password field can not be empty!"),
        Length(min=8, max=60,
               message="Password length should be atleast 8 characters!"),
        check_slash])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(message="Confirm password field can not be empty!"),
        EqualTo('password', message="Password mismatch"), check_slash])
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is already taken!")


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(
        message="Email field can not be empty!"),
        Length(min=5, max=30), Email(), check_slash])
    password = PasswordField("Password", validators=[DataRequired(
        message="Password field can not be empty!"),
        Length(min=8, max=60,
               message="Password length should be atleast 8"), check_slash])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class FileForm(FlaskForm):
    price = SelectField("Price", validators=[DataRequired()])
    prize = SelectField("Prize", validators=[DataRequired()])
    date = DateField("Draw Date", validators=[DataRequired()])
    location = StringField("Draw Location", validators=[DataRequired()])
    number = IntegerField("Draw Number", validators=[DataRequired()])
    name = FileField("Upload Results", validators=[
                     DataRequired(), FileAllowed(["txt"])])
    submit = SubmitField("Upload")

    def validate_location(self, location):
        if location.data.isdigit():
            raise ValidationError("Invalid input!")

    def validate_prize(self, prize):
        bond_prize = Prize.query.filter_by(prize=prize.data).first()
        if not bond_prize:
            raise ValidationError("Please select the valid prize.")


class WinningBondForm(FlaskForm):
    denomination = SelectField("Select Denomination")
    prize = SelectField("Prize")
    serial = TextAreaField("Serial No", validators=[DataRequired(),
                                                    check_slash])
    date = DateField("Draw Date", validators=[DataRequired()])
    location = StringField("Draw Location", validators=[DataRequired()])
    number = IntegerField("Draw Number", validators=[DataRequired()])
    submit = SubmitField("Add")

    def validate_prize(self, prize):
        bond_prize = Prize.query.filter_by(prize=prize.data).first()
        if not bond_prize:
            raise ValidationError("Please select the valid prize.")

    def validate_location(self, location):
        if location.data.isdigit():
            raise ValidationError("Invalid input!")

    def validate_serial(self, serial):
        serials = normalize_serials(serial.data)
        for normalized_serial in serials:
            if not normalized_serial.isdigit():
                raise ValidationError("Invalid serials")
            if len(normalized_serial) != 6:
                raise ValidationError(
                    "Serials must contain exactly six digits.")
