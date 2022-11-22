from flask import Flask, render_template, request, url_for, redirect, jsonify

import json
from flask import jsonify
import hashlib
from db_connection import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'never back down'


@app.route('/', endpoint='from_auth')
@app.route('/index')
def index():
    if request.cookies.get('user') is None:  # Редиректим на страницу регистрации
        return render_template('auth.html')
    else:
        return render_template('index.html', login=request.cookies.get('user'))


@app.route('/rega')
def rega():
    return render_template('rega.html')

@app.route('/rega_admin')
def rega_admin():
    login = "admin"
    password = "1"
    response = "Админ добавлен"
    # Вставляем пользователя в БД
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            password = hashlib.sha256(password.encode() + "_".encode() + app.config['SECRET_KEY'].encode()).hexdigest()
            cur.execute("INSERT INTO users (login,pass) VALUES (?,?)", (login, password))
            con.commit()
            cur.close()
        except sqlite3.Error as error:
            con.rollback()
            response = "Админ уже добавлен"
    return response

@app.route('/handlers/rega_h', methods=['POST'])
def rega_h():
    errors = list()
    login = request.json['login'].strip()
    if login.lower() == "admin":
        errors.append(2)
        return json.dumps({'errors': errors, 'login': login})

    password = request.json['pass'].strip()
    pass_repeat = request.json['pass_repeat'].strip()

    if ((len(login) == 0 or len(password) == 0 or len(pass_repeat) == 0) or
            password != pass_repeat):
        errors.append(1)

    # Вставляем пользователя в БД
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            password = hashlib.sha256(password.encode() + "_".encode() + app.config['SECRET_KEY'].encode()).hexdigest()
            cur.execute("INSERT INTO users (login,pass) VALUES (?,?)", (login, password))
            con.commit()
            cur.close()
        except sqlite3.Error as error:
            con.rollback()
            errors.append(2)  # Логин уже существует
            login = ""
            print("Ошибка базы данных", error)

    return json.dumps({'errors': errors, 'login': login})

@app.route('/auth')
def auth():
    if request.cookies.get('user') is not None:  # Пользователь уже авторизован
        return redirect(url_for('from_auth'), 301)  # Редиректим на главную страницу
    else:
        return render_template('auth.html')  # Показываем страницу авторизации


@app.route('/handlers/auth_h', methods=['POST'])
def auth_h():
    login = request.json['login'].strip()
    password = request.json['pass'].strip()

    errors = list()

    if len(login) == 0 or len(password) == 0:
        errors.append(1)

    # Вставляем пользователя в БД
    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            passhash_from_client = hashlib.sha256(
                password.encode() + "_".encode() + app.config['SECRET_KEY'].encode()).hexdigest()
            cur.execute("SELECT * FROM users WHERE login=? AND pass=?", (login, passhash_from_client))
            con.commit()
            records = cur.fetchall()

            if len(records) == 0:  # Пароли не совпадают или логина такого нет
                errors.append(2)

            cur.close()
        except sqlite3.Error as error:
            con.rollback()
            errors.append(3)  # Неизвестная ошибка
            login = ""
            print("Ошибка базы данных", error)

    return json.dumps({'errors': errors, 'login': login})


@app.route('/logs')
def logs():
    if request.cookies.get('user').lower() != "admin": #Защита
        return "Неизвестная ошибка"

    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM logs")
            con.commit()
            records = cur.fetchall()

            cur.close()
        except sqlite3.Error as error:
            con.rollback()
            print("Ошибка базы данных", error)
        return render_template('logs.html', logs=records)  # Показываем страницу регистрации

@app.route('/users')
def users():
    if request.cookies.get('user').lower() != "admin": #Защита
        return "Неизвестная ошибка"

    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute("SELECT id, login, date FROM users")
            con.commit()
            records = cur.fetchall()

            cur.close()
        except sqlite3.Error as error:
            con.rollback()
            print("Ошибка базы данных", error)
        return render_template('users.html', users=records)  # Показываем страницу регистрации


@app.route('/handlers/clear_logs_h', methods=['POST'])
def clear_logs():
    code = 0

    with sqlite3.connect('database.db') as con:
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM logs")
            con.commit()
            cur.close()
        except sqlite3.Error as error:
            con.rollback()
            code = 1
            print("Ошибка базы данных", error)
        return json.dumps({'code': code})
