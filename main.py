from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user, login_required, UserMixin
#from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'thisissecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

@app.route("/")
def index():
  return render_template('title.html')
    
@app.route('/home')
def home():
  name = session["name"]
  return render_template('home.html', name=name)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method =='POST':
    session.permanent = True
    email = request.form['email']
    password = request.form['password']

    found_user = User.query.filter_by(email=email).first()
    check_password = User.query.filter_by(password=password).first()
    if found_user and check_password:
      session["email"] = email
      session["name"]  = User.query.filter_by(email=email).first().name
      return redirect(url_for('home'))
    else:
      flash("入力された内容では登録がありません。ご確認ください。")
      return redirect(url_for('login'))
    
  else:
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'GET':
    return render_template('signup.html')
  else:
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
  
    found_user = User.query.filter_by(email=email).first()

    if found_user:
      flash('アカウントが既に存在しています。')
      return redirect(url_for('signup'))

    else:
      new_user = User(email=email, name=name, password=password)
    
      #add new user
      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=8080)