from flask_wtf import *
from wtforms import *
from wtforms.validators import *


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Ваш никэйм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[
        DataRequired()])
    about = TextAreaField('Немного о себе', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    submit = SubmitField('Применить')


class ChangeForm(FlaskForm):
    title = StringField('Никнэйм', validators=[DataRequired()])
    content = TextAreaField('Немного о себе')
    submit = SubmitField('Применить')
