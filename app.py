from datetime import datetime
import datetime
import os
import hashlib
from typing import TextIO
from flask_moment import Moment

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

# open('dataHandler.py')
# import json
# hash = hashlib.md5(b'Holka19129')
# print(hash.hexdigest())

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
moment = Moment(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(36), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    developer = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(36))
    avatar = db.Column(db.String(400))

    def __repr__(self):
        return '<User %r>' % self.name


global three
three = datetime.timedelta(hours=3)
from datetime import datetime
blogtime = datetime.utcnow() + three


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(80), unique=True, nullable=False)
    tag = db.Column(db.String(80))
    text = db.Column(db.TEXT, nullable=False)
    data = db.Column(db.DateTime, default=blogtime)

    def __repr__(self):
        return '<Post %r>' % self.id


def log(type, text):
    log: TextIO = open('log.txt', 'a')
    if type == 1:
        log.write('[ERROR] {}\n'.format(text))
        print('ok')


def is_auth():
    if session.get('is_auth') == True:
        return True
    else:
        return False


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
        except db.except_ as error:
            log(1, 'Error in auth query! (114 line)')
        formpass = request.form['password']
        hash_pass = hashlib.md5(str(formpass).encode())
        password = hash_pass.hexdigest()

        if user is None:
            message = 'Такого пользователя не существует!'
            return render_template('auth.html', message=message)

        elif user.password == password:
            session['is_auth'] = True
            session['user_name'] = user.name
            session['user_id'] = user.id
            return redirect('/ucp')

        else:
            message = 'Пароль неверный!'
            return render_template('auth.html', message=message)
    else:
        title = 'Авторизация'
        return render_template('auth.html', title=title)


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        developer = request.form['developer']
        language = request.form['language']
        email = request.form['email']

        hash_pass = hashlib.md5(request.form['password'])
        password = hash_pass.hexdigest()

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
    if not is_auth():
        return redirect('/auth')
    else:
        user: object = User.query.filter(User.id == session['user_id']).first()
        return render_template('ucp/index.html', user=user)


@app.route('/update-user', methods=['POST', 'GET'])
def update_user():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        hash_pass = hashlib.md5(request.form['password'])
        password = hash_pass.hexdigest()

        try:
            user = User.query.get(session['user_id'])
            user.name = name
            user.age = age
            user.email = email
            user.password = password
            db.session.add(user)
            db.session.commit()
            session['user_name'] = name
            return redirect('/ucp')
        except db.except_ as error:
            log(1, '154 line | ' + error)
            print(error)


@app.route('/ucp/logout')
def logout():
    session['is_auth'] = False
    session.pop('user_name', None)
    session.pop('user_id', None)
    return redirect('/')


@app.route('/blog')
def posts():
    global posts
    global users
    title = 'Блог'
    try:
        posts = Blog.query.order_by(Blog.id.desc()).all()
        users = User.query.all()
    except db.except_:
        log(1, 'Ошибка при запросе в бд (206 line)')
    return render_template('blog/posts.html', posts=posts, title=title, three=three, users=users)


@app.route('/blog/<int:id>')
def post(id):
    global post
    try:
        post = Blog.query.filter(Blog.id == id).first()
    except db.except_:
        log(1, 'Ошибка при запросе в бд (215 line)')
    return render_template('blog/post.html', post=post, title=post.title)


@app.route('/blog/<int:id>/edit', methods=['POST', 'GET'])
def edit_post(id):
    if not is_auth():
        return redirect('/auth')
    else:
        global post
        try:
            post = Blog.query.filter(Blog.id == id).first()
        except db.except_:
            log(1, 'Ошибка при запросе в бд (228 line)')

        if request.method == 'POST':
            title = request.form['title']
            text = request.form['text']
            tag = request.form['tag']

            blog = Blog.query.get(id)
            blog.title = title
            blog.text = text
            blog.tag = tag

            try:
                db.session.add(blog)
                db.session.commit()
                return redirect('/blog')
            except db.except_:
                log(1, '245 line ERROR')
    if session['user_id'] == post.user_id:
        return render_template('blog/edit.html', post=post, title='Редактирование')
    else:
        return redirect('/blog/{}'.format(id))


@app.route('/blog/<int:id>/delete')
def del_post(id):
    try:
        blog = Blog.query.get(id)
        db.session.delete(blog)
        db.session.commit()
        return redirect('/blog')
    except:
        return 'delete post' + id


@app.route('/blog/add', methods=['POST', 'GET'])
def add_post():
    if not is_auth():
        return redirect('/auth')
    else:
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['text']
            tag = request.form['tag']

            global Blog
            blog = Blog(title=title, text=text, tag=tag,
                        user_id=session['user_id'])

            try:
                db.session.add(blog)
                db.session.commit()
                return redirect('/blog')
            except db.except_:
                log(1, '252 line ERROR')
        else:
            return render_template('blog/add.html', title='Новый пост')


if __name__ == "__main__":
    app.run(debug=True)
