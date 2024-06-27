from flask import Flask, render_template, request, redirect, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import os
from instance.DataBase import *
import requests
from tlbot import *
from flask_mail import Mail, Message

"""
СДЕЛАТЬ ПОЧТУ ЕСЛИ TG == 0
"""

app = Flask(__name__)
app.secret_key = '79d77d1e7f9348c59a384d4376a9e53f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'static/img'
db.init_app(app)
manager = LoginManager(app)

app.config['MAIL_SERVER']='smtp.mail.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'maks.giskin@mail.ru'
app.config['MAIL_DEFAULT_SENDER'] = 'maks.giskin@mail.ru'
app.config['MAIL_PASSWORD'] = '3PsAkfBDTiUfay9Zb7ME'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    con = Count.query.filter_by(id=1).first()
    users = len(User.query.all())
    probs = len(Problems.query.filter_by(status_problem=1).all())
    if con is None:
        count_all = Count(count_all=1)
        db.session.add(count_all)
        db.session.commit()
        return render_template("index.html",count=count_all,users=users, probs=probs)
    else:
        con.count_all += 1
        db.session.commit()
    return render_template("index.html",count=con,users=users, probs=probs)

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/profile/<int:id>')
def profile(id):
    user = User.query.filter_by(id=id).first()
    user_problems = Problems.query.filter_by(id_user=id).all()
    active_problems = []
    for id_p in user.acvite_problem.split():
        active_problems.append(Problems.query.filter_by(id=int(id_p)).first())
    return render_template("profile.html", user=user, user_problems=user_problems, active_problems=active_problems)

@app.route('/sign-up', methods=["POST", "GET"])
def sign_up():
    if request.method == "GET":
        return render_template("sign-up.html")
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    fio = request.form.get('F') + " " + request.form.get('I') + " " + request.form.get('O')
    user = User.query.filter_by(email=email).first()
    if len(email) > 50:
        flash("Слишком длинный логин")
        return render_template("sign-up.html")
    if user is not None:
        flash('Имя пользователя занято!')
        return render_template("sign-up.html")

    if password != password2:
        flash("Пароли не совпадают!")
        return render_template("sign-up.html")
    try:
        hash_pwd = generate_password_hash(password)
        new_user = User(email=email, password=hash_pwd, fio=fio, admin=0)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")

    except:
        flash("Возникла ошибка при регистрации")
        return render_template("sign-up.html")

@app.route('/problems', methods=["POST", "GET"])
def problems():
    problems = Problems.query.filter_by(status_problem=-1).all()
    return render_template("problems.html", problems=problems)
"""
status_problem
-1 - активная(ждёт решения админа)
0 - ждёт подтверждения пользователя
1 - решена
"""
@app.route('/problem/<int:id>', methods=["POST", "GET"])
def problem(id):
    if current_user == None:
        flash("Войдите в аккаунт")
        return redirect('/')
    problem = Problems.query.filter_by(id=id).first()
    user = User.query.filter_by(id=problem.id_user).first()
    if request.method == "POST":
        solution = request.form.get('solution')
        problem.solution = solution
        problem.status_problem = 0
        user.notif = 1
        flash("")
        db.session.commit()
        flash("Ответ отправлен")
        if user.tg == 0:
            with mail.connect() as conn:
                message = f"На вашу заявку с темой {problem.theme} ответил специалист! \nhttp://127.0.0.1:5000/problem/{id}"
                subject = user.email
                msg = Message(recipients=[subject],
                              body=message,
                              subject=current_user.email)

                conn.send(msg)
        else:
            mes(user.tg)
        return redirect('/')
        # except:
        #     flash("Ошибка при решение проблемы пользователя")
    return render_template("problem.html", problem=problem, user=user)

@app.route('/yes/<int:id>')
def yes(id):
    problem = Problems.query.filter_by(id=id).first()
    user = User.query.filter_by(id=problem.id_user).first()
    flash("Мы рады, что ваш проблема решилась, обращайтесь!")
    problem.status_problem = 1
    problem.acvite_problem = ''
    user.notif = 0
    db.session.commit()
    return redirect('/')

@app.route('/no/<int:id>')
def no(id):
    problem = Problems.query.filter_by(id=id).first()
    user = User.query.filter_by(id=problem.id_user).first()
    problem.solution = ''
    problem.status_problem = 1
    user.notif = 0
    flash("Заявка отправлена на пересмотрение админу")
    db.session.commit()
    return redirect('/')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                flash('Неверный логин или пароль')
        else:
            flash('Такого пользователя не существует')
    return render_template("login.html")

@app.route('/add_problem', methods=["POST", "GET"])
def add_problem():
    if request.method == "POST":
        theme = request.form.get('theme')
        problem = request.form.get('problem')
        user = User.query.filter_by(id=current_user.id).first()
        try:
            if user.acvite_problem == "":
                user.acvite_problem = str(len(Problems.query.all())+1)
            else:
                user.acvite_problem += " " + str(len(Problems.query.all())+1)
            pr = Problems(id_user=user.id, theme=theme, problem=problem)
            db.session.add(pr)
            db.session.commit()
            flash("оставлена заявка")
            return render_template("index.html")
        except:
            flash("Возникла ошибка при подачи заявки")
    return render_template("add_problem.html")


@app.route('/admin_status_p', methods=["POST", "GET"])
def admin_status_p():
    if request.method == "POST":
        email = request.form.get('username_give')
        user = User.query.filter_by(email=email).first()
        if current_user.admin == 2:
            try:
                if 0 <= user.admin <= 2:
                    if user.admin == 2:
                        flash("Пользователь уже является главный администратором")
                        return render_template("admin_status_p.html")
                    elif user.admin == 1:
                        user.admin = 2
                        db.session.commit()
                        flash("Вы сделали пользователя админом второго уровня")
                        return render_template("admin_status_p.html")
                    elif user.admin == 0:
                        user.admin = 1
                        db.session.commit()
                        flash("Вы сделали пользователя админом первого уровня")
                        return render_template("admin_status_p.html")
                else:
                    flash("Error1")
                    return render_template("admin_status_p.html")
            except:
                flash("Error2")
                return render_template("admin_status_p.html")
        return redirect("/")
    return render_template("admin_status_p.html")


@app.route('/admin_status_m', methods=["POST", "GET"])
def admin_status_m():
    if request.method == "POST":
        email = request.form.get('username_give')
        user = User.query.filter_by(email=email).first()

        if current_user.admin == 2:
            try:
                if 0 <= user.admin <= 2:
                    if user.admin == 2:
                        user.admin = 1
                        db.session.commit()
                        flash("Вы сделали пользователя админом первого уровня")
                        return render_template("admin_status_m.html")
                    elif user.admin == 1:
                        user.admin = 0
                        db.session.commit()
                        flash("Вы забрали статус админа у данного пользователя")
                        return render_template("admin_status_m.html")
                    elif user.admin == 0:
                        flash("пользователь уже не имеет статус администратора")
                        return render_template("admin_status_m.html")
                else:
                    flash("Error1")
                    return render_template("admin_status_m.html")
            except:
                flash("Error2")
                return render_template("admin_status_m.html")
        return redirect("/")
    return render_template("admin_status_m.html")



@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
    #executor.start_polling(dp, skip_updates=True)