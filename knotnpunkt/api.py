import json
from datetime import datetime as dt
from flask import Blueprint, request, abort
from flask_login import login_required, current_user
import segno
from .database.json_encoder import DatabaseEncoder
from .database.db import (
    Benutzer,
    Material,
    Aktion,
    Aktivitaet,
    Kategorie,
    Ausleihe,
    Rolle,
    Adresse
)
from .utils import get_ausleihen_fuer_material
from ._version import __version__

api = Blueprint("api", __name__, template_folder="templates",
                url_prefix="/api")


@api.route('/material')
@login_required
def material_api():
    if request.args.get("id"):
        abort(501)
    material = Material.query.all()
    data = []
    for m in material:
        data.append(DatabaseEncoder.default(m))
        data[-1]["id"] = data[-1]['idMaterial']
    if request.args.get("includeAvailability"):
        ausleihen = get_ausleihen_fuer_material(material)
        for m in data:
            m["verfuegbarkeit"] = [DatabaseEncoder.default(
                a) for a in ausleihen[m['idMaterial']]]
        response = {"url": request.url, "data": data}
        return json.dumps(response, cls=DatabaseEncoder)
    else:
        response = {"url": request.url, "data": data}
        return json.dumps(response, cls=DatabaseEncoder)
    abort(501)


@api.route('/qrcode/generator')
@login_required
def qr_generator():
    print(request.date)
    if not request.args.get("id"):
        abort(404)
    id = request.args.get('id')
    artikel: Material = Material.query.filter_by(idMaterial=id).first()
    if artikel is None:
        abort(404)
    code_string = f"knotnpunkt{__version__}:/{artikel.Kategorie.name}/{id}/\nName: {artikel.name}\nQR-Code erstellt: {dt.now():%d.%m.%Y %R}\nVon {current_user.name} ({current_user.benutzername})"
    print(code_string)
    qrcode = segno.make(content=code_string, micro=False)
    return {"qrcode": qrcode.svg_inline(scale=5), "name": artikel.name}


@api.route("/qrcode/decode", methods=['POST'])
@login_required
def decode_qrcode():
    if not request.data:
        return {"success": False}
    code_string = request.data.decode("utf-8")
    print(code_string)
    if not code_string.startswith('knotnpunkt'):
        print("Falsch")
        return {"success": False}
    data = code_string.replace("\n", "").split("/")
    return {"success": True, "id": data[2]}
