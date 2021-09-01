# Management of requests
# ==========================>

import face_recognition
import cv2
import os
import mysql.connector

path = './images'


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
    return student


def paginationInfo(lim, offs):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    mycursor.execute("SELECT matricule, noms, genre, photo, faculte.designation_fac, departement.designation_dep, " \
                     "promotion.designation_prom, appartenir.annee_academ, finance.solde, workprogram.seance FROM "
                     "student JOIN appartenir ON student.matricule = appartenir.matricule_fk  JOIN promotion ON "
                     "appartenir.promotion_fk = promotion.id_prom JOIN departement ON  promotion.departement_fk = "
                     "departement.id_dep JOIN faculte ON departement.faculte_fk = faculte.id_fac JOIN finance ON "
                     "student.matricule = finance.matricule_fk JOIN workprogram ON student.matricule = "
                     "workprogram.matricule_fk LIMIT %s OFFSET %s", (lim, offs))
    studentsList = mycursor.fetchall()
    mycursor.close()
    return studentsList


def getIdAndImages(way):
    faces = []  # List which will store faces
    faceid = []  # List which will store different id
    for root, directory, filenames in os.walk(way):
        for filename in filenames:  # file will store all the name of each image
            separe = filename.split(".")  # spliting filename by '.'
            id = int(separe[0])  # save just the id given to the image wich is in position [1]
            img_path = os.path.join(root, filename)  # this directly assigns folder name 0,1,...
            img = cv2.imread(img_path)  # reading the path containing image
            faces.append(img)  # Add faces to my list
            faceid.append(id)  # Add the id in our list
        print("liste des id pour chaque face du dataset :", faceid)  # It shows the list containing the Id appended
    return faceid, faces


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:  # nous avons mis try except pour eviter l'erreur de index out of range
            encode = face_recognition.face_encodings(img)[0]
        except IndexError as e:
            print("erreur est :", e)  # Affichage de l'erreur 'index out of range'
        encodeList.append(encode)
        print('encode image list: ', encodeList)
    return encodeList


def RegisterStudent(id, Name, Gender, Faculte, Departement, Promotion, Annee, file):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    if id != "" and Name != "" and Gender != "" and file != "" and Faculte != "" and Departement != "" and Promotion != "":
        cmd = "INSERT INTO student(matricule, noms, genre, photo) VALUES(%s, %s, %s, %s)"
        values = (id, Name, Gender, file)
        mycursor.execute(cmd, values)  # Execute the Commande 1
        cmd1 = """INSERT INTO faculte(designation_fac) VALUES(%s)"""
        value1 = (Faculte,)
        mycursor.execute(cmd1, value1)  # Execute the Commande 1
        cmd2 = """INSERT INTO finance(matricule_fk) VALUES(%s)"""
        value2 = (id,)
        mycursor.execute(cmd2, value2)  # Execute the Commande 1

        mycursor.execute("SELECT id_fac FROM faculte ORDER BY id_fac DESC LIMIT 1")
        idFac = mycursor.fetchone()
        cmd3 = """INSERT INTO departement(designation_dep, faculte_fk) VALUES(%s, %s)"""
        values3 = (Departement, idFac[0])
        mycursor.execute(cmd3, values3)  # Execute the Commande 1

        mycursor.execute("SELECT id_dep FROM departement ORDER BY id_dep DESC LIMIT 1")
        idDep = mycursor.fetchone()
        cmd4 = """INSERT INTO promotion(designation_prom, departement_fk) VALUES(%s, %s)"""
        values4 = (Promotion, idDep[0])
        mycursor.execute(cmd4, values4)  # Execute the Commande 1

        mycursor.execute("SELECT id_prom FROM promotion ORDER BY id_prom DESC LIMIT 1")
        idProm = mycursor.fetchone()
        cmd5 = """INSERT INTO appartenir(annee_academ, promotion_fk, matricule_fk) VALUES(%s, %s, %s)"""
        values5 = (Annee, idProm[0], id)
        mycursor.execute(cmd5, values5)  # Execute the Commande 1

        cmd6 = """INSERT INTO workprogram(matricule_fk) VALUES(%s)"""
        values6 = (id,)
        mycursor.execute(cmd6, values6)  # Execute the Commande 1
        conn.commit()
        print("Information registered successfully in database..!")
    else:
        print("Information not filled", "Please fill informations first...")
        conn.rollback()

# def RegisterStudent(id, Name, Gender, file):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     if id != "" and Name != "" and Gender != "" and file != "":
#         cmd = "INSERT INTO student(matricule, noms, genre, photo) VALUES(%s, %s, %s, %s)"
#         values = (id, Name, Gender, file)
#         mycursor.execute(cmd, values)  # Execute the Commande 1
#         conn.commit()
#         print("Information registered successfully in database..!")
#     else:
#         print("Information not filled", "Please fill informations first...")
#         conn.rollback()


# def RegisterFac(Faculte):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     if Faculte != "":
#         cmd = """INSERT INTO faculte(designation_fac) VALUES(%s)"""
#         values = (Faculte,)
#         mycursor.execute(cmd, values)  # Execute the Commande 1
#         conn.commit()
#         print("Information registered successfully in database..!")
#     else:
#         print("Information not filled", "Please fill informations first...")
#         conn.rollback()
#
#
# def RegisterFincance(id):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     if id != "":
#         cmd = """INSERT INTO finance(matricule_fk) VALUES(%s)"""
#         values = (id,)
#         mycursor.execute(cmd, values)  # Execute the Commande 1
#         conn.commit()
#         print("Information registered successfully in database..!")
#     else:
#         print("Information not filled", "Please fill informations first...")
#         conn.rollback()
#
#
# def RegisterDepartem(Departement):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     if Departement != "":
#         mycursor.execute("SELECT id_fac FROM faculte ORDER BY id_fac DESC LIMIT 1")
#         idFac = mycursor.fetchone()
#         cmd = """INSERT INTO departement(designation_dep, faculte_fk) VALUES(%s, %s)"""
#         values = (Departement, idFac[0])
#         mycursor.execute(cmd, values)  # Execute the Commande 1
#         conn.commit()
#         print("Information registered successfully in database..!")
#     else:
#         print("Information not filled", "Please fill informations first...")
#         conn.rollback()
#
#
# def RegisterProm(Promotion):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     if Promotion != "":
#         mycursor.execute("SELECT id_dep FROM departement ORDER BY id_dep DESC LIMIT 1")
#         idDep = mycursor.fetchone()
#         cmd = """INSERT INTO promotion(designation_prom, departement_fk) VALUES(%s, %s)"""
#         values = (Promotion, idDep[0])
#         mycursor.execute(cmd, values)  # Execute the Commande 1
#         conn.commit()
#         print("Information registered successfully in database..!")
#     else:
#         print("Information not filled", "Please fill informations first...")
#         conn.rollback()
#
#
# def RegisterAnnee(id, Annee):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     if id != "" and Annee != "":
#         mycursor.execute("SELECT id_prom FROM promotion ORDER BY id_prom DESC LIMIT 1")
#         idProm = mycursor.fetchone()
#         cmd = """INSERT INTO appartenir(annee_academ, promotion_fk, matricule_fk) VALUES(%s, %s, %s)"""
#         values = (Annee, idProm[0], id)
#         mycursor.execute(cmd, values)  # Execute the Commande 1
#         conn.commit()
#         print("Information registered successfully in database..!")
#     else:
#         print("Information not filled", "Please fill informations first...")
#         conn.rollback()
#
#
# def RegisterWps(id):
#     conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
#     mycursor = conn.cursor()
#     if id != "":
#         cmd = """INSERT INTO workprogram(matricule_fk) VALUES(%s)"""
#         values = (id,)
#         mycursor.execute(cmd, values)  # Execute the Commande 1
#         conn.commit()
#         print("Information registered successfully in database..!")
#     else:
#         print("Information not filled", "Please fill informations first...")
#         conn.rollback()


def deleteStudent(id):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    cmdDel1 = "DELETE FROM student WHERE matricule = %s"
    mycursor.execute(cmdDel1, [id])
    cmdDel2 = "DELETE FROM workprogram WHERE id = %s"
    mycursor.execute(cmdDel2, [id])
    cmdDel3 = "DELETE FROM finance WHERE id = %s"
    mycursor.execute(cmdDel3, [id])
    cmdDel4 = "DELETE FROM appartenir WHERE promotion_fk = %s"
    mycursor.execute(cmdDel4, [id])
    student = conn.commit()
    print("record deleted with success...")
    return student


def takePic(id, name):
    video = cv2.VideoCapture(0)
    while True:
        check, frame = video.read()
        cv2.imshow("Capturing... ", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            cv2.destroyAllWindows()
            break
        elif key == ord('c'):
            cv2.imwrite(os.path.join(path, str(id) + '.' + name + '.jpg'), frame)
            cv2.destroyAllWindows()
            break
    cv2.destroyAllWindows()
    video.release()
