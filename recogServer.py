import base64
import mysql
from flask import Flask, render_template, request, Response, url_for, flash
from flask_paginate import get_page_parameter, Pagination
import myRequests
from camera import VideoCamera
import json

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
static_url_path = '/static'
app.secret_key = 'key secret'

# db = test.db

path = './photos'
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


@app.route('/attendance')
def attendancePart():
    return render_template('attendance.html')


@app.route('/streaming')
def recognitionPart():
    return render_template('streamingPage.html')


@app.route('/registered', methods=['POST', 'GET'])
def registeredSt():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    studentsList = paginationInfo(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=total, css_framework='bootstrap4')
    return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


@app.route('/presenceList', methods=['POST', 'GET'])
def PresenceList():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    presenceList = listePresence(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=len(presenceList), css_framework='bootstrap4')
    return render_template('listePresence.html', studentList=presenceList, pagination=pagination, page=page)


@app.route('/supervisorList', methods=['POST', 'GET'])
def supervisorList():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    supervisorList = listeSuivie(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=len(supervisorList), css_framework='bootstrap4')
    return render_template('supervisorList.html', supervisorList=supervisorList, pagination=pagination, page=page)


@app.route('/recognition')
def reconnaissance():
    return render_template('recognitionOne.html')


@app.route("/recognitionInfo", methods=['POST', 'GET'])
def recognitionInfo():
    if request.method == 'POST':
        cours = request.form["course"]
        salle = request.form["room"]
        superviseur = request.form["supervisor"]
        date = request.form["dateActivity"]
        if request.form["submit"] == "Save":
            myRequests.recognitionInfo(cours, salle, superviseur, date)
    return render_template('streamingPage.html')


@app.route("/registerInfo", methods=['POST', 'GET'])
def registerStudent():
    if request.method == 'POST':
        Matricule = request.form["id"]
        Noms = request.form["noms"]
        Genre = request.form["genre"]
        Faculte = request.form["faculte"]
        Departement = request.form["departement"]
        Promotion = request.form["promotion"]
        Annee = request.form["annee"]
        files = request.files["file"]
        file = files.read()
        if request.form["submit"] == "SaveInfo":
            myRequests.RegisterStudent(Matricule, Noms, Genre, Faculte, Departement, Promotion, Annee, file)
            flash(' ' + Noms + ' was successfully added')

    # Pagination management
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    studentsList = paginationInfo(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=total, css_framework='bootstrap4')
    return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


# This part returns picture and name by entering the id
# =====================================================
# @app.route('/attendances', methods=['POST', 'GET'])
# def attendance():
#     if request.method == 'POST':
#         matr = request.form['matri']
#         x = VideoCamera()
#         _, ident = x.get_frame1()
#         image, name = myRequests.getImageFromDB(ident)
#         imagEncode = base64.b64encode(image).decode('utf-8')
#         return render_template('attendance.html', image=imagEncode, name=name)


@app.route("/registerInfo/<int:id>", methods=['POST', 'GET'])
def deleteStudent(id):
    if request.method == 'POST':
        if request.form["submit"] == "delete":
            myRequests.deleteStudent(id)
            flash(' with ID ' + str(id) + ' was deleted successfully in the database..:)')
    # Pagination management
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    studentsList = paginationInfo(limit, offset)
    pagination = Pagination(page=page, per_page=limit, total=total, css_framework='bootstrap4')
    return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


@app.route("/editInfo", methods=['POST', 'GET'])
def editStudent():
    if request.method == 'POST':
        Matricule = request.form["idEdit"]
        Noms = request.form["nomsEdit"]
        Faculte = request.form["faculteEdit"]
        Departement = request.form["departementEdit"]
        Promotion = request.form["promotionEdit"]
        Annee = request.form["anneeEdit"]
        files = request.files["fileEdit"]
        file = files.read()
        if request.form['submit'] == "SaveEdit":
            myRequests.editStudent(Matricule, Noms, Faculte, Departement, Promotion, Annee, file)
            flash(' ' + Noms + '\'s informations was updated successfully..:)')
    # Pagination management
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    studentsList = paginationInfo(limit, offset)
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
        conn.close()
        pagination = Pagination(page=page, per_page=limit, total=len(studentsList), css_framework='bootstrap4')
        return render_template('studentInfo.html', student=studentsList, pagination=pagination, page=page)


# endpoint for search in presence
@app.route('/filterPresence', methods=['POST', 'GET'])
def searchPresence():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    if request.method == "POST":
        keyWord = request.form['recherche']
        # search by signature or matricule
        conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM liste_presence WHERE matricule_fk LIKE %s OR signature LIKE %s LIMIT %s "
                         "OFFSET %s", ("%" + keyWord + "%", "%" + keyWord + "%", limit, offset))
        studentsList = mycursor.fetchall()
        conn.close()
        pagination = Pagination(page=page, per_page=limit, total=len(studentsList), css_framework='bootstrap4')
        return render_template('listePresence.html', studentList=studentsList, pagination=pagination, page=page)


# endpoint for search in supervisor
@app.route('/supervisorFilter', methods=['POST', 'GET'])
def searchSupervisor():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = page * limit - limit
    if request.method == "POST":
        keyWord = request.form['recherche']
        # search by supervisor name or examen name
        conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")
        mycursor = conn.cursor()
        mycursor.execute("SELECT * FROM suivie_examen WHERE examen_du_jour LIKE %s OR salle LIKE %s OR superviseur "
                         "LIKE %s LIMIT %s OFFSET %s", ("%" + keyWord + "%", "%" + keyWord + "%", "%" + keyWord +
                                                        "%", limit, offset))
        supervisorList = mycursor.fetchall()
        conn.close()
        pagination = Pagination(page=page, per_page=limit, total=len(supervisorList), css_framework='bootstrap4')
        return render_template('supervisorList.html', supervisorList=supervisorList, pagination=pagination, page=page)


def paginationInfo(lim, offs):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    mycursor.execute("SELECT matricule, noms, genre, photo, faculte.designation_fac, departement.designation_dep, "
                     "promotion.designation_prom, appartenir.annee_academ, finance.solde, workprogram.seance, "
                     "FROM student JOIN appartenir ON student.matricule = appartenir.matricule_fk  JOIN promotion ON "
                     "appartenir.promotion_fk = promotion.id_prom JOIN departement ON promotion.departement_fk = "
                     "departement.id_dep JOIN faculte ON departement.faculte_fk = faculte.id_fac JOIN finance ON "
                     "student.matricule = finance.matricule_fk JOIN workprogram ON student.matricule = "
                     "workprogram.matricule_fk LIMIT %s OFFSET %s", (lim, offs))
    studentsList = mycursor.fetchall()
    conn.close()
    return studentsList


def listePresence(lim, offs):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM liste_presence LIMIT %s OFFSET %s", (lim, offs))
    presenceInfo = mycursor.fetchall()
    conn.close()
    return presenceInfo


def listeSuivie(lim, offs):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM suivie_examen LIMIT %s OFFSET %s", (lim, offs))
    suivieInfo = mycursor.fetchall()
    conn.close()
    return suivieInfo


def generator(camer):
    while True:
        frame = camer.get_recognition()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/stream')
def video_feed2():
    return Response(generator(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


# This router returns the graphics
@app.route('/dashboard')
def dashboard():
    facultes, soldes, presenceListe = myRequests.statisticInfo()
    return render_template('dashboard.html', facultes=json.dumps(facultes), soldes=json.dumps(soldes),
                           presenceList=json.dumps(presenceListe))


def gen(camer):
    while True:
        frame = camer.get_attendance()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/recognizing')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
