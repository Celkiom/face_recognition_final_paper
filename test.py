from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pymysql
import mysql.connector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:''@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.Integer, unique=True, nullable=False)
    fullName = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String(255), nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
    promotion = db.relationship('Promotion', backref=db.backref('promotions', lazy=True))

    def __init__(self, matricule, noms, genre, photo):
        self.matricule = matricule
        self.fullName = noms
        self.gender = genre
        self.picture = photo

    def __repr__(self):
        return f'{self.matricule, self.nom}'


class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solde = db.Column(db.Float, default=15)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)


    def __init__(self, solde):
        self.solde = solde

    def __repr__(self):
        return f'{self.solde}'


class WorkProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seance = db.Column(db.Float, default=0)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref=db.backref('students', lazy=True))

    def __init__(self, seance):
        self.seance = seance

    def __repr__(self):
        return f'{self.seance}'


class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(100), nullable=False)

    def __init__(self, designation):
        self.designation = designation

    def __repr__(self):
        return f'{self.designation}'


class Departement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(100), nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.id'), nullable=False)
    promotion = db.relationship('Promotion', backref=db.backref('promotions', lazy=True))

    def __init__(self, designation):
        self.designation = designation

    def __repr__(self):
        return f'{self.designation}'


class Faculte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(100), nullable=False)
    departement_id = db.Column(db.Integer, db.ForeignKey('departement.id'), nullable=False)
    departement = db.relationship('Departement', backref=db.backref('departements', lazy=True))

    def __init__(self, designation):
        self.designation = designation

    def __repr__(self):
        return f'{self.designation}'


class Presence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    salle = db.Column(db.String(100), nullable=False)
    examen = db.Column(db.String(100), nullable=False)
    superviseur = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref=db.backref('students', lazy=True))

    def __init__(self, date, salle, examen, superviseur):
        self.date = date
        self.salle = salle
        self.examen = examen
        self.superviseur = superviseur

    def __repr__(self):
        return f'{self.date, self.salle, self.examen, self.superviseur}'


db.create_all()  # In case user table doesn't exists already. Else remove it.
