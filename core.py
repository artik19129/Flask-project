import os
import datetime
from typing import TextIO

from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

# open('dataHandler.py')
# import json

app = Flask(__name__, template_folder="client-side")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'a0219210_flask'),
    os.getenv('DB_PASSWORD', '19129'),
    os.getenv('DB_HOST', 'artik-life.ru'),
    os.getenv('DB_NAME', 'a0219210_flask')
)
db = SQLAlchemy(app)
app.secret_key = 'jjjdhgasgjkdfwehfsdhfjsdf'
app.permanent_session_lifetime = datetime.timedelta(hours=1)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(36), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    developer = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(36))

    def __repr__(self):
        return '<User %r>' % self.name


def log(type, text):
    log: TextIO = open('log.txt', 'a')
    if type == 1:
        log.write('[ERROR] {}\n'.format(text))
        print('ok')


@app.route('/')
def index():
    title = 'Главная'
    return render_template('index.html', title=title)


@app.route('/users')
def users():
    global users
    title = 'Пользователи'
    try:
        users = User.query.all()
    except db.except_:
        log(1, 'Ошибка при запросе в бд (67 line)')
    return render_template('users.html', users=users, title=title)


@app.route('/user/<int:id>')
def user(id):
    global user
    try:
        user = User.query.filter(User.id == id).first()
    except db.except_:
        log(1, 'Ошибка при запросе в бд (71 line)')
    return render_template('user.html', user=user)


@app.route('/search', methods=['POST', 'GET'])
def search():
    users = User.query.all()
    if request.method == 'POST':
        name = request.form['name']
        for user in users:
            if user.name == name:
                return redirect('/user/{}'.format(user.id))
        return redirect('/users')
    else:
        return redirect('/users')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    global user
    if request.method == 'POST':
        try:
            user = User.query.filter(User.name == request.form['name']).first()
        except db.except_:
            log(1, 'Error in auth query! (97 line)')
            print('Error in auth query!')

        if user is None:
            message = 'Логин или пароль не верный!'
            return render_template('auth.html', message=message)

        elif user.password == request.form['password']:
            print('Успешно!')
            session['is_auth'] = True
            session['user_name'] = user.name
            session['user_id'] = user.id
            return redirect('/ucp')
    else:
        title = 'Авторизация'
        return render_template('auth.html', title=title)


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        age = request.form['age']
        sex = request.form['sex']
        developer = request.form['developer']
        language = request.form['language']
        email = request.form['email']

        user: User = User(name=name, password=password, email=email, age=age, sex=sex, developer=developer,
                          language=language)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/auth')
        except db.except_:
            log(1, '133 line ERROR')
    else:
        title = 'Регистрация'
        return render_template('reg.html', title=title)


@app.route('/ucp')
def ucp():
    if not session['is_auth']:
        return redirect('/auth')
    else:
        user: object = User.query.filter(User.id == session['user_id']).first()
        return render_template('ucp/index.html', user=user)


@app.route('/ucp/logout')
def logout():
    session['is_auth'] = False
    session.pop('user_name', None)
    session.pop('user_id', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
