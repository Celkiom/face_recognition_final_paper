import cv2
import numpy as np
import face_recognition
from myRequests import getIdAndImages, findEncodings, studentInformation, signAttendance, openDoor

Name = ''
identifList = []  # this takes id returns by face and filter them to avoid double insertion in DB


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    path = './photos'
    idDB = []  # List which will store all id from DB
    idList, images = getIdAndImages(path)  # Returns ID and Images
    encodeImgKnown = findEncodings(images)  # takes images encodes
    Student = studentInformation()  # Stores all the information from DB

    def process_attendance(self, img):
        imgReduced = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgReduced = cv2.cvtColor(imgReduced, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgReduced)  # Find and extract face position in the image
        # encodeCurFrame contains a unic encoding facial features that can be compared to any other picture of a face!
        encodesCurFrame = face_recognition.face_encodings(imgReduced, facesCurFrame)
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            # Compare distance between known face and face from camera. It returns distance in %
            faceDis = face_recognition.face_distance(self.encodeImgKnown, encodeFace)
            distance = list(faceDis)  # Converts an array to a list
            print('Equart de ressemblance ', distance)
            minDistance = min(distance)  # Get the min value in the list
            print('distance minimal :', minDistance)
            if minDistance <= 0.40:  # we fix the lentency to 40%
                minIndex = np.argmin(faceDis)  # Get the index of the min element in the array.
                print('Index minimal : ', minIndex)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                for rows in self.Student:
                    self.idDB.append(rows[0])  # Add id from DB to the list idDB
                    newIdDB = set(self.idDB)  # Filter the stand-in element in the list
                    identifiant = self.idList[minIndex]  # Takes one ID corresponding to the index
                    print('indentifiant similaire ', identifiant)
                    if identifiant not in newIdDB:
                        cv2.putText(img, "Unknown face ..!", (40, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    else:
                        for val in self.Student:
                            if val[0] == identifiant:  # check if id from dataset are in DB
                                signAttendance(identifiant)
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                        cv2.putText(img, f"Attendance was taken successfully", (x1 - 90, y2 + 15),
                                    cv2.FONT_HERSHEY_COMPLEX_SMALL, .8, (77, 255, 140), 2)
            else:
                cv2.putText(img, "Unknown face need Registration", (30, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255),
                            2)
        cv2.putText(img, "The light must be good in front", (20, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (200, 0, 40), 1)

        return img

    # ================================================================================================================

    def process_recognition(self, img):
        imgReduced = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgReduced = cv2.cvtColor(imgReduced, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgReduced)  # Find and extract face position in the image
        # encodeCurFrame contains a unic encoding facial features that can be compared to any other picture of a face!
        encodesCurFrame = face_recognition.face_encodings(imgReduced, facesCurFrame)
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            # Compare distance between known face and face from camera. It returns distance in %
            faceDis = face_recognition.face_distance(self.encodeImgKnown, encodeFace)
            distance = list(faceDis)  # Converts an array to a list
            print('Equart de ressemblance ', distance)
            minDistance = min(distance)  # Get the min value in the list
            print('distance minimal :', minDistance)
            if minDistance <= 0.40:  # we fix the lentency to 40%
                minIndex = np.argmin(faceDis)  # Get the index of the min element in the array.
                print('Index minimal : ', minIndex)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)

                for rows in self.Student:
                    self.idDB.append(rows[0])  # Add id from DB to the list idDB
                    newIdDB = set(self.idDB)  # Filter the stand-in element in the list
                    identif = self.idList[minIndex]  # Takes one ID corresponding to the index
                    print('indentifiant similaire ', identif)
                    if identif not in newIdDB:
                        cv2.putText(img, "Unknown face ..!", (40, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
                    else:
                        for val in self.Student:
                            if val[0] == identif and val[8] >= 15 and val[9] >= 15:  # check if id from folder are in DB
                                global identifList
                                if identif not in identifList:
                                    identifList.append(identif)
                                    openDoor(identif)  # Method that allows to open door
                                else:
                                    print('Vous avez deja signe la presence =::=')
                                global Name
                                Name = val[1]
                                y1, x2, y2, x1 = faceLoc
                                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
                                cv2.putText(img, f"Welcome {Name}", (x1 - 50, y2 + 15), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                            .9, (45, 240, 114), 2)
                            # else:
                            #     cv2.putText(img, "You're not allowed", (170, 430), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            else:
                cv2.putText(img, "Unknown face need Registering ..!", (30, 100), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (0, 0, 255), 2)
        cv2.putText(img, "The light must be good in front", (20, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (200, 0, 40), 1)

        return img

    # ===================================================================================================================

    def get_attendance(self):
        success, data = self.video.read()
        frame = self.process_attendance(data)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_recognition(self):
        success, datas = self.video.read()
        frame = self.process_recognition(datas)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
