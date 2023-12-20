from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from blog.models import User


class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired("Campo Obbligatorio!")])
    password = PasswordField('Password',
                        validators=[DataRequired("Campo Obbligatorio!")])
    remember_me = BooleanField('Ricordami')
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title = StringField('Titolo',
                        validators=[DataRequired("Campo Obbligatorio!"), Length(min=3, max=120, message="Assicurati che il titolo abbia tra i 3 e i 120 caratteri.")])
    description = TextAreaField('Descrizione',
                        validators=[Length(max=240, message="Assicurati che il campo descrizione non superi i 240 caratteri.")])
    body = TextAreaField('Contenuto',
                        validators=[DataRequired("Campo Obbligatorio!")])
    image = FileField('Copertina Articolo',
                        validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Pubblica Post')


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')


class CityForm(FlaskForm):
    city = StringField('city',
                    validators=[DataRequired("Campo Obbligatorio!")])


class ContactForm(FlaskForm):
    name = StringField('Nome', validators=[
                    DataRequired('Il nome non può essere vuoto ')])
    email = StringField('E-mail', validators=[DataRequired('email non può essere vuota '),
                        Email('Inserisci un''e-mail valida ')])
    subject = StringField('Soggetto', validators=[
                        DataRequired('oggetto non può essere vuoto ')])
    message = TextAreaField('Messaggio', validators=[
                        DataRequired('Messaggio non può essere vuoto')])
    submit = SubmitField("Invia Richiesta")
