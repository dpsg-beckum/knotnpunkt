import json
from flask import Blueprint, request, abort, jsonify
from flask_login import login_required
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


api = Blueprint("api", __name__, template_folder="templates", url_prefix="/api")


@api.route('/material')
@login_required
def material_api():
    print("API!!!")
    if request.args.get(id):
        abort(501)
    else:
        material = Material.query.all()
    print(material)
    result = []
    for m in material:
        result.append({
            "id": m.idMaterial,
            "name": m.name,
            "title": m.name,
            "Eigenschaften": json.loads(m.Eigenschaften),
            "idKategorie": m.Kategorie_idKategorie,
            "Kategorie": m.Kategorie.name,
        })
    response = {"url": request.url, "result": result}
    return jsonify(response)