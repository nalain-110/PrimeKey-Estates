from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, SubmitField,
                     BooleanField, IntegerField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo,
                                Optional, NumberRange, ValidationError)
from app.models import User


class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(0, 20)])
    role = SelectField('Register As',
                       choices=[(3, 'Client'), (2, 'Agent')],
                       coerce=int)
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 200)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(0, 20)])
    # Agent-only fields (shown only for agents in the template)
    agency_name = StringField('Agency Name', validators=[Optional(), Length(0, 150)])
    license_no = StringField('License No.', validators=[Optional(), Length(0, 100)])
    experience_years = IntegerField('Experience (years)',
                                    validators=[Optional(), NumberRange(0, 60)])
