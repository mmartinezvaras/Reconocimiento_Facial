import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime

video_caprure = cv2.VideoCapture(0,cv2.CAP_AVFOUNDATION)  

messi_image = face_recognition.load_image_file("photos/messi.png")
messi_face_encoding = face_recognition.face_encodings(messi_image)[0]

cr7_image = face_recognition.load_image_file("photos/cr7.png")
cr7_face_encoding = face_recognition.face_encodings(cr7_image)[0]

lisa_image = face_recognition.load_image_file("photos/lisa.png")
lisa_face_encoding = face_recognition.face_encodings(lisa_image)[0]

theRock_image = face_recognition.load_image_file("photos/theRock.png")
theRock_face_encoding = face_recognition.face_encodings(theRock_image)[0]

will_image = face_recognition.load_image_file("photos/will.png")
will_face_encoding = face_recognition.face_encodings(will_image)[0]

known_face_encodings = [
    messi_face_encoding,
    cr7_face_encoding,
    lisa_face_encoding,
    theRock_face_encoding,
    will_face_encoding
]

known_face_names = [
    "Messi",
    "Cristiano Ronaldo",
    "Lisa",
    "The Rock",
    "Will Smith"
]

students = known_face_names.copy()

face_locations = []
face_encodings = []
face_names = []
s = True

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")

# "a" añade registros sin borrar los anteriores
openFile = open(current_date + ".csv", "a", newline="")
Inwriter = csv.writer(openFile)

while True:
    ret, frame = video_caprure.read()

    if not ret or frame is None:
        print("Error: no se pudo obtener imagen de la cámara.")
        break

    small_frame = cv2.resize(
        frame,
        (0, 0),
        fx=0.25,
        fy=0.25
    )

    rgb_small_frame = cv2.cvtColor(
        small_frame,
        cv2.COLOR_BGR2RGB
    )

    if s:
        face_locations = face_recognition.face_locations(
            rgb_small_frame
        )

        face_encodings = face_recognition.face_encodings(
            rgb_small_frame,
            face_locations
        )

        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                known_face_encodings,
                face_encoding
            )

            name = ""

            face_distance = face_recognition.face_distance(
                known_face_encodings,
                face_encoding
            )

            best_match_index = np.argmin(face_distance)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

            if name in known_face_names:
                if name in students:
                    students.remove(name)

                    print("Personas pendientes:", students)

                    current_time = datetime.now().strftime("%H-%M-%S")

                    Inwriter.writerow([name, current_time])

                    openFile.flush()

                    print(
                        "Asistencia registrada:",
                        name,
                        current_time
                    )

    cv2.imshow("Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_caprure.release()
cv2.destroyAllWindows()
openFile.close()