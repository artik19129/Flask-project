from flask import Flask, render_template, url_for

# import json

app = Flask(__name__, template_folder="client-side")

# Не получилось реализовать подгрузку базы данных из json файла
# with open('users.json') as json_users:
#     users = json.load(json_users)

students = [
    {"id": 0, "name": "Sanka", "age": "16", "sex": 1, "developer": 1, "language": "Python"},
    {"id": 1, "name": "Artem", "age": "16", "sex": 1, "developer": 1, "language": "JavaScript"},
    {"id": 2, "name": "Vasya", "age": "19", "sex": 1, "developer": 1, "language": "Java"},
    {"id": 3, "name": "Ilya", "age": "14", "sex": 1, "developer": 0, "language": "None"},
    {"id": 4, "name": "Masha", "age": "15", "sex": 0, "developer": 1, "language": "Ruby"},
]


@app.route('/')
def index():
    title = 'Главная'
    return render_template('index.html', title=title)


@app.route('/users')
def users():
    title = 'Пользователи'
    return render_template('users.html', users=students, title=title)


@app.route('/user/<int:id>')
def user(id):
    return render_template('user.html', user=students[id])


if __name__ == "__main__":
    app.run(debug=True)
