"""Forms for SPORKY app."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class Favorites(FlaskForm):
    """Save recipe form."""
    used = BooleanField('Have you prepared this dish in the past?')

    # dropdown menu
    rating = SelectField('How would you rate this recipe? (if you have prepared it; if not, leave as 0))', 
                         choices=[('0', '0'),('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    notes = TextAreaField('(Optional) Notes')

   

