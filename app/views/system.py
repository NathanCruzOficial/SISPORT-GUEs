# app/routes.py (ou onde ficam suas rotas)
from flask import Blueprint, Response, render_template
from app import camera
import time

system_bp = Blueprint("system", __name__)

def generate_frames():
    while True:
        frame = camera.get_frame()
        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        else:
            time.sleep(0.05)  # ← aguarda se frame não estiver pronto

        time.sleep(1 / 30)  # ← limita a 30fps

@system_bp.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@system_bp.route("/identify")
def identify():
    return render_template("identify.html")
