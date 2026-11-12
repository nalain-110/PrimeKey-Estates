from flask_wtf import FlaskForm
from wtforms import TextAreaField, FloatField, SelectField, SubmitField, StringField, DateTimeLocalField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class InquiryForm(FlaskForm):
    message = TextAreaField('Your Message', validators=[DataRequired(), Length(10, 1000)])
    submit  = SubmitField('Send Inquiry')


class OfferForm(FlaskForm):
    offered_price = FloatField('Your Offer (PKR)', validators=[DataRequired(), NumberRange(min=1)])
    notes         = TextAreaField('Additional Notes', validators=[Optional(), Length(0, 500)])
    submit        = SubmitField('Submit Offer')


class SiteVisitForm(FlaskForm):
    scheduled_date = StringField('Preferred Date & Time', validators=[DataRequired()])
    notes          = TextAreaField('Additional Notes', validators=[Optional(), Length(0, 300)])
    submit         = SubmitField('Schedule Visit')


class ContactForm(FlaskForm):
    name    = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email   = StringField('Email', validators=[DataRequired(), Length(5, 120)])
    phone   = StringField('Phone', validators=[Optional(), Length(0, 20)])
    subject = StringField('Subject', validators=[Optional(), Length(0, 200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(10, 1000)])
    submit  = SubmitField('Send Message')


class NewsletterForm(FlaskForm):
    email  = StringField('Email Address', validators=[DataRequired(), Length(5, 120)])
    submit = SubmitField('Subscribe')
