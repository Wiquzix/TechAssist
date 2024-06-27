from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    fio = db.Column(db.String)
    admin = db.Column(db.Integer, default=0)
    acvite_problem = db.Column(db.String, default="")
    tg = db.Column(db.Integer, default=0)
    notif = db.Column(db.Integer)
class Problems(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer)
    theme = db.Column(db.String)
    problem = db.Column(db.String)
    solution = db.Column(db.String)
    status_problem = db.Column(db.Integer, default=-1)

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    teacher = db.Column(db.String, nullable=False)

class Count(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count_all = db.Column(db.Integer, default=1)




