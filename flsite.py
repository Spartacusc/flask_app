import sqlite3
import os
from flask import Flask, render_template, url_for, request, flash, redirect, session, abort, g
from FDataBase import FDataBase

# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'sdfasdfsdf234235235'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


def connect_db():
    # путь из конфига
    conn = sqlite3.connect(app.config['DATABASE'])
    # возвращение значений в словаре, а не кортежах
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    # соединение с бд, если оно еще не установлено
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    # закрываем соединение с бд, если оно было установлено
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<alias>")
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


# @app.route("/about")
# def about():
#     return render_template('about.html', title="about site", menu=menu)


@app.route("/profile/<username>")
def profile(username: str):
    if 'userLogger' not in session or session['userLogger'] != username:
        abort(401)
    return f" Профиль пользователя: {username.capitalize()}"


# @app.route("/contact", methods=["POST", "GET"])
# def contact():
#     if request.method == 'POST':
#         if len(request.form['username']) > 2:
#             flash('Сообщение отправлено', category='success')
#         else:
#             flash('Ошибка отправки', category='error')
#     return render_template('contact.html', title="Обратная связь", menu=menu)


# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if 'userLogger' in session:
#         return redirect(url_for('profile', username=session['userLogger']))
#     elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
#         session['userLogger'] = request.form['username']
#         return redirect(url_for('profile', username=session['userLogger']))
#
#     return render_template('login.html', title="Авторизация", menu=menu)


@app.errorhandler(404)
def pageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page404.html', title="Страница не найдена", menu=dbase.getMenu()), 404


@app.errorhandler(401)
def pageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page401.html', title="Ошибка доступа", menu=dbase.getMenu()), 401


if __name__ == '__main__':
    app.run(debug=True)
