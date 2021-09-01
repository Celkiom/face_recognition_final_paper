from base64 import b64encode
import cv2
import mysql
from flask import Flask, render_template, request, Response, url_for, flash
from flask_paginate import get_page_parameter, Pagination
import myRequests
from camera import VideoCamera
import test

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
static_url_path = '/static'

db = test.db

path = './images'
img_path = []
# for pagination
limit = 5  # perPage

rows = myRequests.studentInformation()
total = len(rows)


@app.route('/')
@app.route('/authentication')
def login():
    return render_template('authentication.html')


@app.route('/index')
@app.route('/welcome')
def index():
    return render_template('index.html')


@app.route('/registered', methods=['POST', 'GET'])
def registeredSt():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    studentsList = myRequests.paginationInfo(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=total, css_framework='bootstrap4')
    return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


@app.route("/registerInfo", methods=['POST', 'GET'])
def registerStudent():
    if request.method == 'POST':
        if not request.form['id'] or not request.form['noms'] or not request.form['genre'] or not request.form['faculte'] or not request.form['departement'] or not request.form['promotion'] or not request.files['file']:
            flash('Ples enter all the fields', 'error')
        else:
            Matricule = request.form["id"]
            Noms = request.form["noms"]
            Genre = request.form["genre"]
            Faculte = request.form["faculte"]
            Departement = request.form["departement"]
            Promotion = request.form["promotion"]
            Annee = request.form["annee"]
            files = request.files["file"]
            file = str(files)
            # etudiantOb = test.Etudiant(matricule=Matricule, nom=Noms, genre=Genre, photo=file)
            # studentObj = test.Student(Matricule, Noms, Genre, file)
        if request.form["submit"] == "SaveInfo":
            myRequests.RegisterStudent(Matricule, Noms, Genre, Faculte, Departement, Promotion, Annee, file)
            # myRequests.RegisterFac(Faculte)
            # myRequests.RegisterFincance(Matricule)
            # myRequests.RegisterDepartem(Departement)
            # myRequests.RegisterProm(Promotion)
            # myRequests.RegisterAnnee(Matricule, Annee)
            # myRequests.RegisterWps(Matricule)

            # promotionOb = test.Promotion.query.all().first()

            # db.session.add(studentObj)
            # db.session.commit()

            flash('Reccord was successfully added')

    # Pagination management
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    studentsList = myRequests.paginationInfo(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=total, css_framework='bootstrap4')
    return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


@app.route('/recognition')
def reconnaissance():
    return render_template('recognitionOne.html')


@app.route('/attendance')
def attendanceFinger():
    return render_template('attendance.html')


@app.route("/studentInfo/<int:id>", methods=['POST', 'GET'])
def deleteStudent(id):
    myRequests.deleteStudent(id)
    # Pagination management
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    studentsList = myRequests.paginationInfo(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=total, css_framework='bootstrap4')
    return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


# endpoint for search
@app.route('/filterStudent', methods=['POST', 'GET'])
def search():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    if request.method == "POST":
        keyWord = request.form['recherche']
        # search by name or id
        conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")
        mycursor = conn.cursor()
        mycursor.execute("SELECT matricule, noms, genre, photo, faculte.designation_fac, departement.designation_dep, " \
                         "promotion.designation_prom, appartenir.annee_academ, finance.solde, workprogram.seance FROM "
                         "student JOIN appartenir ON student.matricule = appartenir.matricule_fk  JOIN promotion ON "
                         "appartenir.promotion_fk = promotion.id_prom JOIN departement ON  promotion.departement_fk = "
                         "departement.id_dep JOIN faculte ON departement.faculte_fk = faculte.id_fac JOIN finance ON "
                         "student.matricule = finance.matricule_fk JOIN workprogram ON student.matricule = "
                         "workprogram.matricule_fk WHERE student.matricule LIKE %s OR noms LIKE %s OR genre LIKE %s "
                         "LIMIT %s OFFSET %s", ("%" + keyWord + "%", "%" + keyWord + "%", keyWord, limit, offset))
        studentsList = mycursor.fetchall()
        mycursor.close()
        pagination = Pagination(page=page, per_page=limit, css_framework='bootstrap4')
        return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


# def gen(camer):
#     while True:
#         frame = camer.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# @app.route('/streaming')
# def video_feed():
#     # return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')
#     return render_template("streamingPage.html")

def gen(camer):
    while True:
        frame = camer.get_frame2()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/recognizing')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
