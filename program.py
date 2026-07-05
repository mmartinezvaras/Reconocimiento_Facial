import csv
import sys
import warnings
from datetime import datetime
from pathlib import Path

import cv2

warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API.*",
    category=UserWarning,
    module="face_recognition_models",
)
import face_recognition
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
PHOTOS_DIR = BASE_DIR / "photos"
PEOPLE = {
    "Messi": "messi.png",
    "Cristiano Ronaldo": "cr7.png",
    "Lisa": "lisa.png",
    "The Rock": "theRock.png",
    "Will Smith": "will.png",
}
FRAME_SCALE = 0.25


def load_known_faces() -> tuple[list[np.ndarray], list[str]]:
    """Carga una codificacion facial por persona y explica cualquier foto invalida."""
    encodings: list[np.ndarray] = []
    names: list[str] = []

    for name, filename in PEOPLE.items():
        photo_path = PHOTOS_DIR / filename
        if not photo_path.is_file():
            raise FileNotFoundError(f"No se encuentra la foto de {name}: {photo_path}")

        image = face_recognition.load_image_file(photo_path)
        faces = face_recognition.face_encodings(image)
        if not faces:
            raise ValueError(f"No se ha detectado ningún rostro en {photo_path.name}.")

        encodings.append(faces[0])
        names.append(name)

    return encodings, names


def open_camera() -> cv2.VideoCapture:
    backend = cv2.CAP_AVFOUNDATION if sys.platform == "darwin" else cv2.CAP_ANY
    camera = cv2.VideoCapture(0, backend)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(
            "No se pudo abrir la cámara. Comprueba sus permisos y que otra aplicación no la esté usando."
        )
    return camera


def draw_faces(
    frame: np.ndarray,
    locations: list[tuple[int, int, int, int]],
    names: list[str],
) -> None:
    inverse_scale = round(1 / FRAME_SCALE)
    for (top, right, bottom, left), name in zip(locations, names):
        top, right, bottom, left = (
            top * inverse_scale,
            right * inverse_scale,
            bottom * inverse_scale,
            left * inverse_scale,
        )
        color = (46, 184, 135) if name != "Desconocido" else (70, 70, 220)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
        cv2.putText(
            frame,
            name,
            (left + 6, bottom - 8),
            cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (255, 255, 255),
            1,
        )


def run() -> None:
    known_encodings, known_names = load_known_faces()
    pending = set(known_names)
    csv_path = BASE_DIR / f"{datetime.now():%Y-%m-%d}.csv"
    camera = open_camera()

    face_locations: list[tuple[int, int, int, int]] = []
    face_names: list[str] = []
    process_frame = True

    try:
        with csv_path.open("a+", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            csv_file.seek(0, 2)
            if csv_file.tell() == 0:
                writer.writerow(["Nombre", "Hora"])
                csv_file.flush()

            print("Cámara activa. Pulsa q para salir.")
            while True:
                success, frame = camera.read()
                if not success or frame is None:
                    raise RuntimeError("Se perdió la conexión con la cámara.")

                if process_frame:
                    small_frame = cv2.resize(
                        frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE
                    )
                    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame)
                    current_encodings = face_recognition.face_encodings(
                        rgb_frame, face_locations
                    )
                    face_names = []

                    for encoding in current_encodings:
                        distances = face_recognition.face_distance(
                            known_encodings, encoding
                        )
                        best_index = int(np.argmin(distances))
                        matches = face_recognition.compare_faces(
                            known_encodings, encoding
                        )
                        name = (
                            known_names[best_index]
                            if matches[best_index]
                            else "Desconocido"
                        )
                        face_names.append(name)

                        if name in pending:
                            pending.remove(name)
                            current_time = datetime.now().strftime("%H:%M:%S")
                            writer.writerow([name, current_time])
                            csv_file.flush()
                            print(f"Asistencia registrada: {name} a las {current_time}")
                            print("Personas pendientes:", sorted(pending) or "ninguna")

                process_frame = not process_frame
                draw_faces(frame, face_locations, face_names)
                cv2.imshow("Sistema de asistencia - pulsa q para salir", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        run()
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
