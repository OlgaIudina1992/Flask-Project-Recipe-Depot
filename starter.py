from flask import Flask, redirect, render_template, flash, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import MetaData, or_
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager,  login_required, logout_user, current_user
from webforms import LoginForm, RecipeForm, SearchForm, UserForm, NameForm
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "my secret key"

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

##Login Functionality

#Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                flash("Login Successful")
                return redirect(url_for('dashboard'))                
            else:
                flash("Incorrect Password")
        else:
            flash("S-User Does Nor Exist")

    return render_template('login.html', form=form)

#Logout Route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You are Logged Out")
    return redirect(url_for('login'))

#Dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    
    return render_template('dashboard.html')

##Recipes

#Recipe collection route
@app.route('/recipes')
def recipes():
    recipes = Recipes.query.order_by(Recipes.date_posted)
    return render_template('recipes.html', recipes=recipes)

#Individual recipe route
@app.route('/recipes/<int:id>')
def recipe_page(id):
    recipe = Recipes.query.get_or_404(id)
    return render_template('recipe_page.html', recipe=recipe)

#Add recipe route
@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        poster = current_user.id
        recipe = Recipes(
            title = form.title.data, 
            ingredients = form.ingredients.data, 
            recipe = form.recipe.data,
            poster_id = poster,
            slug = form.slug.data)
        form.title.data = ''
        form.ingredients.data = ''
        form.recipe.data = ''
        form.slug.data = ''        

        db.session.add(recipe)
        db.session.commit()
        flash("Recipe Added Successfully!")

    return render_template('add_recipe.html', form=form)   

#Edit recipe route
@app.route('/recipes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def recipe_edit(id):
    recipe = Recipes.query.get_or_404(id)
    form = RecipeForm()
    if form.validate_on_submit():
            recipe.title = form.title.data 
            recipe.ingredients = form.ingredients.data 
            recipe.recipe = form.recipe.data            
            recipe.slug = form.slug.data

            db.session.add(recipe)
            db.session.commit()
            flash("Recipe Updated!") 
            return redirect(url_for('recipes', id = recipe.id))

    if current_user.id == recipe.poster.id:
        form.title.data = recipe.title
        form.ingredients.data = recipe.ingredients
        form.recipe.data = recipe.recipe    
        form.slug.data = recipe.slug
        return render_template('recipe_edit.html', form=form)
    else:
        flash("Recipe Cannot Be Updated!") 
        return redirect(url_for('recipes', id = recipe.id))
    
#Delete recipe route
@app.route('/recipes/delete/<int:id>')
@login_required
def recipe_delete(id):
    recipe_deleted = Recipes.query.get_or_404(id)
    id = current_user.id
    if id == recipe_deleted.poster.id:
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
    else:
        flash("Recipe Cannot Be Deleted!")
        recipes = Recipes.query.order_by(Recipes.date_posted)
        return render_template('recipes.html', recipes=recipes)
        
## Users 

#Add user route
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

#Update user route
@app.route('/update/<int:id>', methods=["GET", "POST"])
@login_required
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

#Delete user route
@app.route('/delete/<int:id>')
@login_required
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

##Various

#Navbar Data
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

#Search route
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    recipes = Recipes.query
    if form.validate_on_submit():
        recipe_searchbar = form.searchbar.data
        recipes = recipes.filter(or_(Recipes.title.like('%' + recipe_searchbar + '%'), 
                                     Recipes.recipe.like('%' + recipe_searchbar + '%'), 
                                     Recipes.ingredients.like('%' + recipe_searchbar + '%')))
        recipes = recipes.order_by(Recipes.title).all()
        return render_template('search.html', form=form, searchbar=recipe_searchbar, recipes = recipes)

#Home route
@app.route('/')
def index():
    return render_template('index.html')

#Name and errors
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

#Converter route
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

##Models

class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    ingredients = db.Column(db.Text)
    recipe = db.Column(db.Text)
    author = db.Column(db.String(256))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(256))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    favorite_dish = db.Column(db.String(200))
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    recipes = db.relationship('Recipes', backref='poster')

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
    
