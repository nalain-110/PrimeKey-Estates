from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
import re


class BlogForm(FlaskForm):
    title        = StringField('Blog Title', validators=[DataRequired(), Length(5, 200)])
    excerpt      = StringField('Short Excerpt', validators=[Optional(), Length(0, 300)])
    content      = TextAreaField('Content (HTML allowed)', validators=[DataRequired()])
    cover_image  = FileField('Cover Image', validators=[FileAllowed(['jpg','jpeg','png','webp','gif'], 'Images only!')])
    is_published = BooleanField('Publish Now')
    submit       = SubmitField('Save Blog Post')
