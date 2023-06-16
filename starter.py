from flask import Flask, redirect, render_template, flash, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager,  login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "my secret key"
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    ingredients = db.Column(db.Text)
    recipe = db.Column(db.Text)
    author = db.Column(db.String(256))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(256))

class RecipeForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    ingredients = StringField("List of Ingredients", validators=[DataRequired()], widget=TextArea())
    recipe = StringField("Recipe", validators=[DataRequired()], widget=TextArea())
    author = StringField("Contributor", validators=[DataRequired()])
    slug = StringField("Slugified URL", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/recipes/delete/<int:id>')
def recipe_delete(id):
    recipe_deleted = Recipes.query.get_or_404(id)

    try:
        db.session.delete(recipe_deleted)
        db.session.commit()
        flash("Recipe Deleted!")
        recipes = Recipes.query.order_by(Recipes.date_posted)
        return render_template('recipes.html', recipes=recipes)
    except:
        flash("Recipe Could Not Be Deleted!")        
        recipes = Recipes.query.order_by(Recipes.date_posted)
        return render_template('recipes.html', recipes=recipes)

@app.route('/recipes')
def recipes():
    recipes = Recipes.query.order_by(Recipes.date_posted)
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipes/<int:id>')
def recipe_page(id):
    recipe = Recipes.query.get_or_404(id)
    return render_template('recipe_page.html', recipe=recipe)

@app.route('/recipes/edit/<int:id>', methods=['GET', 'POST'])
def recipe_edit(id):
    recipe = Recipes.query.get_or_404(id)
    form = RecipeForm()
    if form.validate_on_submit():
            recipe.title = form.title.data 
            recipe.ingredients = form.ingredients.data 
            recipe.recipe = form.recipe.data
            recipe.author = form.author.data
            recipe.slug = form.slug.data

            db.session.add(recipe)
            db.session.commit()
            flash("Recipe Updated!") 
            return redirect(url_for('recipes', id = recipe.id))
    form.title.data = recipe.title
    form.ingredients.data = recipe.ingredients
    form.recipe.data = recipe.recipe
    form.author.data = recipe.author
    form.slug.data = recipe.slug

    return render_template('recipe_edit.html', form=form)    

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipes(
            title = form.title.data, 
            ingredients = form.ingredients.data, 
            recipe = form.recipe.data,
            author = form.author.data,
            slug = form.slug.data)
        form.title.data = ''
        form.ingredients.data = ''
        form.recipe.data = ''
        form.author.data = ''
        form.slug.data = ''        

        db.session.add(recipe)
        db.session.commit()
        flash("Recipe Added Successfully!")

    return render_template('add_recipe.html', form=form)   


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    favorite_dish = db.Column(db.String(200))
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    password_hash = db.Column(db.String(150))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #same as __str__(self)
    def __repr__(self):
        return '<Name %r>' % self.name
    
@app.route('/delete/<int:id>')
def delete(id):
    user_deleted = Users.query.get_or_404(id)    
    form = UserForm()
    name = None
    try:
            db.session.delete(user_deleted)
            db.session.commit()
            flash("Deleted Successfully!")
            our_users = Users.query.order_by(Users.date_added)
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
            flash("Failed to Delete User")
            return render_template('add_user.html', form=form, name=name, our_users=our_users)

class UserForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    
    favorite_dish = StringField("Fave Dish: ")    
    email = StringField("Email: ", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash', message='Passwords Must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/update/<int:id>', methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_updated = Users.query.get_or_404(id)
    if request.method == "POST":
        name_updated.name = request.form['name']
        name_updated.favorite_dish = request.form['favorite_dish']
        name_updated.email = request.form['email']
        try:
            db.session.commit()
            flash("Updated Successfully!")
            return render_template('update.html', name_updated=name_updated, form=form)
        except:
            flash("Failed to Update User")
            return render_template('update.html', name_updated=name_updated, form=form)
    else:
        return render_template('update.html', name_updated=name_updated, form=form)

class NameForm(FlaskForm):
    name = StringField("Username: ")
    c_to_f = DecimalField("Converter: ", places=2)
    submit = SubmitField("Submit")

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    name = None
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pass = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name = form.name.data, email=form.email.data, favorite_dish=form.favorite_dish.data, password_hash=hashed_pass)
            db.session.add(user)
            db.session.commit()          
        name = form.name.data
       
        form.name.data = '' 
        form.email.data = '' 
        form.favorite_dish.data =''
        form.password_hash.data =''
        flash("User Added")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None   
    c_to_f = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''    
        c_to_f = (form.c_to_f.data * 9/5) + 32
        form.c_to_f.data = ''      
        flash("Form Submitted!")

    return render_template('name.html', name=name, c_to_f = c_to_f, form=form)
