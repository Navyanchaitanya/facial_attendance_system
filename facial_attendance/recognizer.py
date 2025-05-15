import cv2
import face_recognition
import os
import sys
import numpy as np
from datetime import datetime
import csv

DATASET_DIR = "dataset"
EMBEDDINGS_DIR = "embeddings"
ATTENDANCE_FILE = "attendance.csv"

if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)

if not os.path.exists(EMBEDDINGS_DIR):
    os.makedirs(EMBEDDINGS_DIR)

def save_attendance(name):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Date", "Time"])
    with open(ATTENDANCE_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, date, time])

def register_face(name):
    cam = cv2.VideoCapture(0)
    print("Press 'c' to capture face, 'q' to quit.")
    while True:
        ret, frame = cam.read()
        if not ret:
            continue
        cv2.imshow("Register Face", frame)
        key = cv2.waitKey(1)
        if key == ord('c'):
            path = os.path.join(DATASET_DIR, f"{name}.jpg")
            cv2.imwrite(path, frame)
            face_encodings = face_recognition.face_encodings(frame)
            if face_encodings:
                np.save(os.path.join(EMBEDDINGS_DIR, f"{name}.npy"), face_encodings[0])
                print("Face saved.")
                break
        elif key == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()

def recognize_faces():
    known_encodings = []
    known_names = []

    for file in os.listdir(EMBEDDINGS_DIR):
        if file.endswith(".npy"):
            encoding = np.load(os.path.join(EMBEDDINGS_DIR, file))
            known_encodings.append(encoding)
            known_names.append(file.replace(".npy", ""))

    cam = cv2.VideoCapture(0)
    message = "⚠️ No face detected"
    marked = False

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        if not encodings:
            cv2.imshow("Attendance", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        for encoding, location in zip(encodings, locations):
            matches = face_recognition.compare_faces(known_encodings, encoding)
            face_distances = face_recognition.face_distance(known_encodings, encoding)
            name = "Unknown"

            if True in matches:
                best_match = np.argmin(face_distances)
                if matches[best_match]:
                    name = known_names[best_match]
                    save_attendance(name)
                    message = f"✅ Attendance marked for {name}"
                    marked = True
            else:
                message = "❌ Face not matched. Attendance not marked."

            top, right, bottom, left = location
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Attendance", frame)
        cv2.waitKey(2000)
        break

    cam.release()
    cv2.destroyAllWindows()

    with open("last_message.txt", "w", encoding="utf-8") as f:
        f.write(message)



if __name__ == "__main__":
    if sys.argv[1] == "register":
        register_face(sys.argv[2])
    elif sys.argv[1] == "recognize":
        recognize_faces()
