from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "my secret key"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    favorite_dish = db.Column(db.String(200))
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

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
    name = StringField("User: ", validators=[DataRequired()])
    favorite_dish = StringField("Fave Dish: ")    
    email = StringField("Email: ", validators=[DataRequired()])      
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
            user = Users(name = form.name.data, email=form.email.data, favorite_dish=form.favorite_dish.data)
            db.session.add(user)
            db.session.commit()          
        name = form.name.data
        form.name.data = '' 
        form.email.data = '' 
        form.favorite_dish.data =''
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
