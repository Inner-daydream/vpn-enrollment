"""Provides classes that represent the forms available"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField,EmailField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    """Represents the login form fields"""
    email = EmailField('Email address', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
    