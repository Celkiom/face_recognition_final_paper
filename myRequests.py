# Management of requests
# ==========================>
from base64 import b64decode  # don't remove library from line 3 to 6.
import numpy as np
from io import BytesIO
from PIL import Image
import mysql.connector
import face_recognition
import cv2
import os

# img = 0
# img = bytes(img)
# name = 'nom etudiant :'
path = '../UsersPhotos'


def studentInformation():
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    cmd = "SELECT matricule, noms, genre, photo, faculte.designation_fac, departement.designation_dep, " \
          "promotion.designation_prom, appartenir.annee_academ, finance.solde, workprogram.seance FROM student JOIN " \
          "appartenir ON student.matricule = appartenir.matricule_fk  JOIN promotion ON appartenir.promotion_fk = " \
          "promotion.id_prom JOIN departement ON  promotion.departement_fk = departement.id_dep JOIN faculte ON " \
          "departement.faculte_fk = faculte.id_fac JOIN finance ON student.matricule = finance.matricule_fk JOIN " \
          "workprogram ON student.matricule = workprogram.matricule_fk "
    mycursor.execute(cmd)
    student = mycursor.fetchall()
    conn.close()
    return student


def getIdAndImages(way):
    faces = []  # List which will store faces
    faceid = []  # List which will store different id
    for root, directory, filenames in os.walk(way):
        for filename in filenames:  # file will store all the name of each image
            separe = filename.split(".")  # spliting filename by '.'
            ID = int(separe[0])  # save just the id given to the image wich is in position [1]
            img_path = os.path.join(root, filename)  # this directly assigns folder name 0,1,...
            img = cv2.imread(img_path)  # reading the path containing image
            faces.append(img)  # Add faces to my list
            faceid.append(ID)  # Add the id in our list
        print("liste des id pour chaque face du dataset :", faceid)  # It shows the list containing the Id appended
    return faceid, faces


# def getIdAndImages():
#     faces = []  # List which will store faces
#     faceid = []  # List which will store different id
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     mycursor.execute("SELECT matricule, photo FROM student")
#     data = mycursor.fetchall()
#     for x in data:
#         img = np.array(Image.open(BytesIO(x[1])))  #converting image from db with type byte to array
#         faces.append(img)
#         faceid.append(x[0])
#         # print("liste des face du DB :", faces)  # It shows the list containing the Id appended
#         return faceid, faces


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:  # nous avons mis try except pour eviter l'erreur de index out of range
            encode = face_recognition.face_encodings(img)[0]
        except IndexError as e:
            print("erreur est :", e)  # Affichage de l'erreur 'index out of range'
        encodeList.append(encode)
        # print('encode image list: ', encodeList)
    return encodeList


def recognitionInfo(course, classrom, supervisorName, date):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    cmd = """INSERT INTO suivie_examen(date, salle, examen_du_jour, superviseur) VALUES(%s, %s, %s, %s)"""
    value = (date, classrom, course, supervisorName)
    mycursor.execute(cmd, value)  # Execute the Commande 1
    conn.commit()
    print("supervisor info registered successfully in database..!")
    conn.close()


def RegisterStudent(ID, Name, Gender, Faculty, Department, Promotion, year, file):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    Cursor = conn.cursor()
    if ID != "" and Name != "" and Gender != "" and file != "" and Faculty != "" and Promotion != "" and year != "":
        cmd = "INSERT INTO student(matricule, noms, genre, photo) VALUES(%s, %s, %s, %s)"
        values = (ID, Name, Gender, file)
        Cursor.execute(cmd, values)  # Execute the Commande 1
        # ========================================================================================
        cmd1 = """INSERT INTO faculte(designation_fac) VALUES(%s)"""
        value1 = (Faculty,)
        Cursor.execute(cmd1, value1)  # Execute the Commande 1
        # ========================================================================================
        cmd2 = """INSERT INTO finance(matricule_fk) VALUES(%s)"""
        value2 = (ID,)
        Cursor.execute(cmd2, value2)  # Execute the Commande 1
        # ========================================================================================
        Cursor.execute("SELECT id_fac FROM faculte ORDER BY id_fac DESC LIMIT 1")
        idFac = Cursor.fetchone()
        cmd3 = """INSERT INTO departement(designation_dep, faculte_fk) VALUES(%s, %s)"""
        values3 = (Department, idFac[0])
        Cursor.execute(cmd3, values3)  # Execute the Commande 1
        # ========================================================================================
        Cursor.execute("SELECT id_dep FROM departement ORDER BY id_dep DESC LIMIT 1")
        idDep = Cursor.fetchone()
        cmd4 = """INSERT INTO promotion(designation_prom, departement_fk) VALUES(%s, %s)"""
        values4 = (Promotion, idDep[0])
        Cursor.execute(cmd4, values4)  # Execute the Commande 1
        # ========================================================================================
        Cursor.execute("SELECT id_prom FROM promotion ORDER BY id_prom DESC LIMIT 1")
        idProm = Cursor.fetchone()
        cmd5 = """INSERT INTO appartenir(annee_academ, promotion_fk, matricule_fk) VALUES(%s, %s, %s)"""
        values5 = (year, idProm[0], ID)
        Cursor.execute(cmd5, values5)  # Execute the Commande 1
        # ========================================================================================
        cmd6 = """INSERT INTO workprogram(matricule_fk) VALUES(%s)"""
        values6 = (ID,)
        Cursor.execute(cmd6, values6)  # Execute the Commande 1
        conn.commit()
        conn.close()
        print("Information registered successfully in database..!")
    else:
        print("Information not filled", "Please fill informations first...")
        conn.rollback()


def deleteStudent(ID):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    mycursor.execute("SELECT noms FROM student WHERE matricule =" + str(ID))
    name = mycursor.fetchone()
    nom = str(ID) + '.' + str(name[0]) + '.jpg'
    print(' le type du nom est', type(nom))
    mycursor.execute("SELECT promotion_fk FROM appartenir WHERE matricule_fk =" + str(ID))
    idprom = mycursor.fetchone()
    mycursor.execute("SELECT departement_fk FROM promotion WHERE id_prom =" + str(idprom[0]))
    iddep = mycursor.fetchone()
    mycursor.execute("SELECT faculte_fk FROM departement WHERE id_dep =" + str(iddep[0]))
    idfac = mycursor.fetchone()
    mycursor.execute("DELETE FROM workprogram WHERE matricule_fk = %s" % ID)
    mycursor.execute("DELETE FROM finance WHERE matricule_fk = %s" % ID)
    mycursor.execute("DELETE FROM liste_presence WHERE matricule_fk = %s" % ID)
    mycursor.execute("DELETE FROM appartenir WHERE matricule_fk = %s" % ID)
    mycursor.execute("DELETE FROM promotion WHERE id_prom = %s" % idprom[0])
    mycursor.execute("DELETE FROM departement WHERE id_dep = %s" % iddep[0])
    mycursor.execute("DELETE FROM faculte WHERE id_fac = %s" % idfac[0])
    mycursor.execute("DELETE FROM student WHERE matricule = %s" % ID)
    students = conn.commit()
    if os.path.exists('./photos/'+nom):
        os.remove('./photos/'+nom)
        print("picture deleted with success...")
    else:
        print("the picture doesn't exist...")
    conn.close()
    print("record deleted with success...")
    return students


def editStudent(ID, nom, faculty, department, promotion, year, file):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    mycursor.execute("SELECT promotion_fk FROM appartenir WHERE matricule_fk =" + str(ID))
    idprom = mycursor.fetchone()
    mycursor.execute("SELECT departement_fk FROM promotion WHERE id_prom =" + str(idprom[0]))
    iddep = mycursor.fetchone()
    mycursor.execute("SELECT faculte_fk FROM departement WHERE id_dep =" + str(iddep[0]))
    idfac = mycursor.fetchone()
    # =======================================================================================
    cmd = "UPDATE student SET noms = %s,photo = %s WHERE matricule =%s"
    value = (nom, file, ID)
    mycursor.execute(cmd, value)
    # =======================================================================================
    com = "UPDATE appartenir SET annee_academ = %s WHERE matricule_fk = %s"
    val = (year, ID)
    mycursor.execute(com, val)
    # ========================================================================================
    cmd1 = "UPDATE faculte SET designation_fac =%s WHERE id_fac =%s"
    value1 = (faculty, idfac[0])
    mycursor.execute(cmd1, value1)
    # ========================================================================================
    cmd2 = "UPDATE departement SET designation_dep =%s WHERE id_dep =%s"
    value2 = (department, iddep[0])
    mycursor.execute(cmd2, value2)
    # ========================================================================================
    cmd3 = "UPDATE promotion SET designation_prom =%s WHERE id_prom =%s"
    value3 = (promotion, idprom[0])
    mycursor.execute(cmd3, value3)
    conn.commit()
    conn.close()


def signAttendance(idEtudiant):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    cmd = """UPDATE liste_presence SET signature =%s WHERE matricule_fk = %s AND signature = %s"""
    value = ('Present', idEtudiant, 'Entree')
    mycursor.execute(cmd, value)  # Execute the Commande 1
    conn.commit()
    conn.close()


def openDoor(idEtudiant):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    cmd1 = """UPDATE liste_presence SET signature =%s WHERE matricule_fk = %s AND signature = %s"""
    value1 = ('Absent', idEtudiant, 'Entree')
    mycursor.execute(cmd1, value1)  # Execute the Commande 1

    cmd2 = """INSERT INTO liste_presence(signature, matricule_fk) VALUES(%s, %s)"""
    value2 = ('Entree', idEtudiant)
    mycursor.execute(cmd2, value2)  # Execute the Commande 1
    conn.commit()
    print("Information registered successfully in database..!")
    conn.close()


# this method returns value that help produce pie graphic
# ========================================================
def participationInfo():
    absent = []
    present = []
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    cmd = "SELECT signature FROM liste_presence"
    mycursor.execute(cmd)
    listPresence = mycursor.fetchall()
    conn.close()
    for presence in listPresence:
        if "Absent" in presence[0]:
            absent.append(presence[0])
        elif "Present" in presence[0]:
            present.append(presence[0])
    return len(absent), len(present)


# This method manager chart diagram graphic and returns value of participationInfo by returning a list of their value
# ====================================================================================================================
def statisticInfo():
    fac = []
    solde = []
    listPresence = []
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    cmd = "SELECT faculte.designation_fac, SUM(finance.solde) FROM student JOIN appartenir ON student.matricule = " \
          "appartenir.matricule_fk  JOIN promotion ON appartenir.promotion_fk = promotion.id_prom JOIN departement ON " \
          "promotion.departement_fk = departement.id_dep JOIN faculte ON departement.faculte_fk = faculte.id_fac JOIN " \
          "finance ON student.matricule = finance.matricule_fk GROUP BY faculte.designation_fac "
    mycursor.execute(cmd)
    statistic = mycursor.fetchall()
    for state in statistic:
        fac.append(state[0])
        solde.append(int(state[1]))
    conn.close()
    absent, present = participationInfo()
    listPresence.append(absent)
    listPresence.append(present)
    return fac, solde, listPresence


def takePic():
    video = cv2.VideoCapture(0)
    while True:
        check, frame = video.read()
        cv2.imshow("Capturing... ", frame)
        key = cv2.waitKey(1)
        if key % 256 == 27:
            cv2.destroyAllWindows()
            break
        elif key % 256 == 32:
            cv2.imwrite(os.path.join(path, 'image.jpg'), frame)

            cv2.destroyAllWindows()
            break
    cv2.destroyAllWindows()
    video.release()

# This method returns image and name from db
# ==========================================
# def getImageFromDB(id):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     mycursor.execute("SELECT noms, photo FROM student WHERE matricule =" + str(id))
#     data = mycursor.fetchall()
#     for x in data:
#         global img
#         img = x[1]
#         global name
#         name = x[0]
#     # print('la photo est de : ', name)
#     # print('la photo est la : ', img)
#     return img, name

# getImageFromDB(2117)
