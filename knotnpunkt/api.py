import json
from flask import Blueprint, request, abort, jsonify
from flask_login import login_required
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
