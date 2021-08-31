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
    cmd = "SELECT matriculeEtudiant, nomsEtudiant, genreEtudiant, faceEtudiant, faculte.designation_fac, " \
          "departement.designation_departem, promotion.designation_prom, appartenir.annee_academ, finance.solde, " \
          "workprogram.seance FROM student JOIN appartenir ON student.matriculeEtudiant = appartenir.matricule_fk" \
          " JOIN promotion ON appartenir.id_promotion_fk = promotion.id_promotion JOIN departement ON" \
          " promotion.departement_fk = departement.id_departement JOIN faculte ON " \
          "departement.faculte_fk = faculte.id_fac JOIN finance ON student.matriculeEtudiant = finance.matricule_fk " \
          "JOIN workprogram ON student.matriculeEtudiant = workprogram.matricule_fk"
    mycursor.execute(cmd)
    student = mycursor.fetchall()
    return student


def paginationInfo(lim, offs):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connect to DB
    mycursor = conn.cursor()
    mycursor.execute("SELECT matriculeEtudiant, nomsEtudiant, genreEtudiant, faceEtudiant, faculte.designation_fac, "
                     "departement.designation_departem, promotion.designation_prom, appartenir.annee_academ, "
                     "finance.solde, workprogram.seance FROM student JOIN appartenir ON student.matriculeEtudiant = "
                     "appartenir.matricule_fk JOIN promotion ON appartenir.id_promotion_fk = promotion.id_promotion "
                     "JOIN departement ON promotion.departement_fk = departement.id_departement JOIN faculte ON "
                     "departement.faculte_fk = faculte.id_fac JOIN finance ON student.matriculeEtudiant = "
                     "finance.matricule_fk JOIN workprogram ON student.matriculeEtudiant = workprogram.matricule_fk "
                     "LIMIT %s OFFSET %s", (lim, offs))
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
    if id != "" and Name != "" and Gender != "" and Faculte != "" and Departement != "" and Promotion != "" and Annee != "" and file != "":
        try:
            mycursor.execute("INSERT INTO student(student.matriculeEtudiant, student.nomsEtudiant, student.genreEtudiant, " \
                       "student.faceEtudiant) VALUES(?,?,?, ?)",(id, Name, Gender, file))  # Execute the Commande 1

            mycursor.execute("INSERT INTO faculte(faculte.designation_fac) VALUES(?)", (Faculte, ))  # Execute the Commande 1

            mycursor.execute("INSERT INTO finance(finance.matricule_fk) VALUES(?)", (id,))  # Execute the Commande 1

            mycursor.execute("INSERT INTO departement(departement.designation_departem, departement.faculte_fk)" \
                   "VALUES(?,?)", (Departement,"SELECT faculte.id_fac FROM faculte ORDER BY id_fac DESC LIMIT 1"))  # Execute the Commande 1

            mycursor.execute("INSERT INTO promotion(promotion.designation_prom, promotion.departement_fk) " \
                   "VALUES(?, ?)",(Promotion,"SELECT departement.id_departement FROM departement ORDER BY id_departement DESC LIMIT 1")) # Execute the Commande 1

            mycursor.execute("INSERT INTO appartenir(appartenir.annee_academ, appartenir.id_promotion_fk, appartenir.matricule_fk) " \
                   "VALUES(?,?,?)", (Annee, "SELECT promotion.id_promotion FROM promotion ORDER BY id_promotion DESC LIMIT 1", id))  # Execute the Commande 1

            mycursor.execute("INSERT INTO workprogram(workprogram.matricule_fk) VALUES(?)",(id,))  # Execute the Commande 1
            conn.commit()

            # mycursor.execute(cmd1, value1)  # Execute the Commande 1
            # conn.commit()
            # mycursor.execute(cmd2, value2)  # Execute the Commande 2
            # conn.commit()
            # mycursor.execute(cmd3, value3)  # Execute the Commande 3
            # conn.commit()
            # mycursor.execute(cmd4, value4)  # Execute the Commande 4
            # conn.commit()
            # mycursor.execute(cmd5, value5)  # Execute the Commande 5
            # conn.commit()
            # mycursor.execute(cmd6, value6)  # Execute the Commande 6
            # conn.commit()
            # mycursor.execute(cmd7, value7)  # Execute the Commande 7
            # conn.commit()
            print("Information registered successfully in database..!")
        except:
            print("Error..! can not add in database..!")
    else:
        print("Information", "Please fill informations first...")
        conn.rollback()


def deleteStudent(id):
    conn = mysql.connector.connect(host="localhost", database="memoire", user="root", password="")  # Connection to DB
    mycursor = conn.cursor()
    cmdDel1 = "DELETE FROM student WHERE student.matriculeEtudiant = %s"
    mycursor.execute(cmdDel1, [id])
    cmdDel2 = "DELETE FROM workprogram WHERE ID = %s"
    mycursor.execute(cmdDel2, [id])
    cmdDel3 = "DELETE FROM finance WHERE ID = %s"
    mycursor.execute(cmdDel3, [id])
    cmdDel4 = "DELETE FROM appartenir WHERE appartenir.id_promotion_fk = %s"
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


