from flask_wtf import Form
from flask_login import current_user
from passlib.handlers.sha2_crypt import sha256_crypt
from wtforms import BooleanField, PasswordField, StringField, RadioField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import validators
from passlib.hash import sha256_crypt
from .util import get_categories
import TruckAPI as t


class RegisterForm(Form):
    username = StringField('Username',
                           [validators.Length(min=4, max=25, message='Username must be between 4 and 25 characters')])
    email = StringField('Email Address', [validators.DataRequired(), validators.Email("Please enter a valid email")])
    password = PasswordField('New Password', [
        validators.InputRequired(),
        validators.Length(6, 20, 'Password is too Short'),
        validators.EqualTo('confirm', message='Passwords must match'),
    ])
    confirm = PasswordField('Repeat Password')
    recommendations = BooleanField('Recieve emails about recommended Food Trucks', [validators.Optional()])

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = t.Users.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        user = t.Users.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        user = t.Users.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('Unknown email')
            return False
        if not sha256_crypt.verify(self.password.data, user.password):
            self.password.errors.append('Incorrect Password')
            return False
        return True


class SettingsForm(Form):
    username = StringField('Username',
                           [validators.Optional(), validators.Length(min=4, max=25, message='Username must be between 4 and 25 characters')])
    email = StringField('Email Address', [validators.Optional(), validators.Email("Please enter a valid email")])
    password = PasswordField('New Password', [
        validators.Optional(),
        validators.Length(6, 20, 'Password is too Short'),
        validators.EqualTo('confirm', message='Passwords must match'),
    ])
    confirm = PasswordField('Repeat Password')
    recommendations = BooleanField('Receive emails about recommended Food Trucks', [validators.Optional()])

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(SettingsForm, self).validate()
        if not initial_validation:
            return False
        if not current_user:
            return False
        if sha256_crypt.verify(self.password.data, current_user.password):
            self.password.errors.append('Password Cannot be the same as your current password')
            return False
        if current_user.username == self.username.data:
            self.username.errors.append('Username Cannot be the same as your last username')
            return False
        if current_user.email == self.email.data:
            self.email.errors.append('Email Cannot be the same as your last email')
            return False
        return True


class RatingForm(Form):
    speed = RadioField('Speed', choices=[('0.6', ''), ('1.2', ''), ('1.8', ''), ('2.4', ''), ('3', '')])
    quality = RadioField('Quality', choices=[('0.6', ''), ('1.2', ''), ('1.8', ''), ('2.4', ''), ('3', '')])
    Value = RadioField('Value', choices=[('0.6', ''), ('1.2', ''), ('1.8', ''), ('2.4', ''), ('3', '')])
    comment = StringField('Comment', validators=[validators.Optional(),
                                                 validators.Length(max=280, message="Your comment cannot be greater "
                                                                                    "than 280 Characters")])
    truck = HiddenField(validators=[validators.DataRequired()])

    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(RatingForm, self).validate()
        if not initial_validation:
            return False
        if not self.comment.data:
            self.comment.data = ''
        if not self.speed.data: self.speed.data = '0'
        if not self.Value.data: self.Value.data = '0'
        if not self.quality.data: self.quality.data = '0'
        return True
