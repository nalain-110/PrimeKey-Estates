from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange


class DealForm(FlaskForm):
    deal_price  = FloatField('Deal Price (PKR)', validators=[DataRequired(), NumberRange(min=1)])
    deal_type   = SelectField('Deal Type', choices=[('Sale', 'Sale'), ('Rent', 'Rent')])
    buyer_id    = SelectField('Buyer', coerce=int, validators=[DataRequired()])
    submit      = SubmitField('Create Deal')

    def set_buyer_choices(self):
        from app.models import User
        clients = User.query.filter_by(role_id=3).all()
        self.buyer_id.choices = [(u.id, f"{u.name} ({u.email})") for u in clients]


class TokenReceiptForm(FlaskForm):
    amount       = FloatField('Token Amount (PKR)', validators=[DataRequired(), NumberRange(min=1)])
    receipt_no   = StringField('Receipt Number', validators=[DataRequired()])
    notes        = TextAreaField('Notes', validators=[Optional()])
    submit       = SubmitField('Issue Receipt')


class InstallmentPlanForm(FlaskForm):
    total_amount       = FloatField('Total Amount (PKR)', validators=[DataRequired()])
    down_payment       = FloatField('Down Payment (PKR)', validators=[Optional(), NumberRange(min=0)], default=0.0)
    installments_count = IntegerField('Number of Installments', validators=[DataRequired(), NumberRange(min=1, max=360)])
    frequency          = SelectField('Frequency', choices=[('Monthly','Monthly'),('Quarterly','Quarterly'),('Yearly','Yearly')])
    start_date         = StringField('Start Date', validators=[DataRequired()])
    submit             = SubmitField('Create Plan')


class CommissionForm(FlaskForm):
    amount = FloatField('Commission Amount (PKR)', validators=[DataRequired(), NumberRange(min=0)])
    rate   = FloatField('Commission Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    status = SelectField('Status', choices=[('Pending','Pending'),('Paid','Paid')])
    submit = SubmitField('Update Commission')
