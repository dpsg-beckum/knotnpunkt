from flask import Blueprint, send_from_directory

ui = Blueprint("ui", __name__)

@ui.route("/")
def base():
    return send_from_directory('frontend/public', 'index.html')

# Endpunkt für alle anderen statischen Dateien (CSS, JS, ...)
@ui.route("/<path:path>")
def home(path):
    return send_from_directory('frontend/public', path)
