from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL


class BookForm(FlaskForm):
    title = StringField(label='Enter book name or author', validators=[DataRequired()])
    submit = SubmitField(label='Search')


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    name = StringField('Your name', validators=[DataRequired()])
    email = StringField('Your Email', validators=[DataRequired()])
    password = PasswordField('Your Password', validators=[DataRequired()])
    submit = SubmitField('Register')

