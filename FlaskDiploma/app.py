import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from wtforms import StringField
from wtforms.fields.simple import SubmitField, PasswordField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'a_simple_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    back_messages = db.Column(db.Integer, default=5)

    conversations = relationship("Conversation", back_populates="user")


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text(), nullable=False, default="")
    ai_response = db.Column(db.Text(), nullable=False, default="")
    user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="conversations")


with app.app_context():
    db.create_all()


class UserInputForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    submit = SubmitField('Send')

class Memory(FlaskForm):
    amount = StringField('amount', validators=[DataRequired()])
    submit = SubmitField('Apply')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('protected'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/', methods=['GET', 'POST'])
@login_required
def protected():
    form = UserInputForm()
    memory_form = Memory()

    if memory_form.validate_on_submit():
        amount = int(memory_form.amount.data)
        current_user.back_messages = amount
        db.session.commit()

    if form.validate_on_submit():
        user_input = form.question.data
        ai_response = get_response(text_=user_input)

        append_conversation(user_input=user_input,
                            ai_response=ai_response,
                            user_id=current_user.id)

    conversation = Conversation.query.filter_by(user_id=current_user.id).all()

    model_response = []
    for convo in conversation[-current_user.back_messages:]:
        model_response.append({
            "user": convo.user_input,
            "ai": convo.ai_response
        })
    print(model_response)

    return render_template('base.html',
                           user=current_user.username,
                           success_message=model_response,
                           form=form,
                           memory_form=memory_form)


@app.route('/logout')
@login_required  # Ensure that only logged-in users can log out
def logout():
    logout_user()  # Log out the current user
    return redirect(url_for('login'))



def append_conversation(user_input, ai_response, user_id):
    new_conversation = Conversation(
        user_input=user_input,
        ai_response=ai_response,
        user_id=user_id
    )
    db.session.add(new_conversation)
    db.session.commit()


def get_response(text_="", cust_sys_=""):
    encoded_text = str(text_)
    encoded_cust_sys = str(cust_sys_)

    port = "8998"

    url = f"http://0.0.0.0:{port}/translate?text={encoded_text}&cust_sys={encoded_cust_sys}"

    try:
        response = requests.get(url)
    except:
        return "Server is down"

    if response.status_code == 200:
        data = response.json()
        return data["ai"]
    else:
        error = f"Server is {response.status_code} - {response.text}"
        return error


if __name__ == '__main__':
    app.run(debug=True, port=9900)
