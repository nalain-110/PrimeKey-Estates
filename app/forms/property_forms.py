from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, TextAreaField, FloatField, IntegerField,
                     SelectField, BooleanField, SubmitField, MultipleFileField)
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class PropertyForm(FlaskForm):
    title        = StringField('Property Title', validators=[DataRequired(), Length(5, 200)])
    description  = TextAreaField('Description', validators=[Optional(), Length(0, 2000)])
    price        = FloatField('Price (PKR)', validators=[DataRequired(), NumberRange(min=1)])
    size         = FloatField('Size', validators=[Optional(), NumberRange(min=0)])
    size_unit    = SelectField('Size Unit', choices=[('Marla','Marla'),('Sq Ft','Sq Ft'),('Kanal','Kanal')])
    bedrooms     = IntegerField('Bedrooms', validators=[Optional(), NumberRange(min=0)], default=0)
    bathrooms    = IntegerField('Bathrooms', validators=[Optional(), NumberRange(min=0)], default=0)
    floors       = IntegerField('Floors', validators=[Optional(), NumberRange(min=1)], default=1)
    year_built   = IntegerField('Year Built', validators=[Optional()], default=2020)
    type_id      = SelectField('Property Type', coerce=int, validators=[DataRequired()])
    listing_type = SelectField('Listing Type', choices=[('Sale','For Sale'),('Rent','For Rent')])
    status       = SelectField('Status', choices=[('Available','Available'),('Sold','Sold'),('Rented','Rented')])
    is_featured  = BooleanField('Mark as Featured')
    is_verified  = BooleanField('Mark as Verified')
    # Location
    city_id      = SelectField('City', coerce=int, validators=[DataRequired()])
    area_id      = SelectField('Area', coerce=int, validators=[Optional()])
    address      = StringField('Full Address', validators=[Optional(), Length(0, 300)])
    map_lat      = FloatField('Latitude', validators=[Optional()], default=31.5204)
    map_lng      = FloatField('Longitude', validators=[Optional()], default=74.3587)
    # Images
    images       = MultipleFileField('Property Images', validators=[FileAllowed(['jpg','jpeg','png','gif','webp'], 'Images only!')])
    submit       = SubmitField('Save Property')

    def set_type_choices(self):
        from app.models import PropertyType
        self.type_id.choices = [(t.id, t.name) for t in PropertyType.query.all()]

    def set_city_choices(self):
        from app.models import City
        self.city_id.choices = [(0, '-- Select City --')] + [(c.id, c.name) for c in City.query.all()]
        self.area_id.choices = [(0, '-- Select Area --')]
