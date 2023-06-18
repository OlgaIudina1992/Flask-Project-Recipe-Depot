from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, DecimalField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


class NameForm(FlaskForm):
    name = StringField("Username: ")
    c_to_f = DecimalField("Converter: ", places=2)
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    
    favorite_dish = StringField("Fave Dish: ")    
    email = StringField("Email: ", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash', message='Passwords Must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

class RecipeForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    ingredients = CKEditorField("List of Ingredients", validators=[DataRequired()])
    recipe = CKEditorField("Recipe", validators=[DataRequired()])
    author = StringField("Contributor")
    slug = StringField("Slugified URL", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    searchbar = StringField("Search", validators=[DataRequired()])
    submit = SubmitField('Submit')