from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, SubmitField,
                     BooleanField, IntegerField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo,
                                Optional, ValidationError, NumberRange)
from app.models import User


def _clean_email(value):
    return value.strip().lower() if value else value


class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email = StringField('Email', validators=[DataRequired(), Email()],
                        filters=[_clean_email])
    phone = StringField('Phone Number', validators=[Optional(), Length(0, 20)])
    role = SelectField('Register As',
                       choices=[(3, 'Client'), (2, 'Agent')],
                       coerce=int)
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 200)])
    # Matches register.html
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],
                        filters=[_clean_email])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email = StringField('Email', validators=[DataRequired(), Email()],
                        filters=[_clean_email])
    phone = StringField('Phone Number', validators=[Optional(), Length(0, 20)])
    # Agent-only fields (optional, ignored for clients)
    agency_name = StringField('Agency Name', validators=[Optional(), Length(0, 150)])
    license_no = StringField('License No.', validators=[Optional(), Length(0, 100)])
    experience_years = IntegerField('Experience (years)',
                                    validators=[Optional(), NumberRange(0, 80)])
    submit = SubmitField('Save Changes')

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id

    def validate_email(self, field):
        clash = User.query.filter(User.email == field.data,
                                  User.id != self.user_id).first()
        if clash:
            raise ValidationError('Email is already used by another account.')
