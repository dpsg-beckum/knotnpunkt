import json
from datetime import datetime as dt
from datetime import timedelta
from flask import (
    abort,
    Blueprint,
    request,
    Response,
    send_file,
)
from flask_login import login_required, current_user
import segno
from ..database import db
from ..database.json_encoder import DatabaseEncoder
from ..database.db import (
    Material,
    Ausleihe,
)
from ..utils import (
    get_ausleihen_fuer_material,
)
from .._version import __version__
from ..export.file_generators import (
    SVGGenerator,
    ExportError,
    PDFGenerator,
)


api_routes = Blueprint("api", __name__, template_folder="templates",
                       url_prefix="")


@api_routes.route('/material')
@login_required
def material_api():
    if request.args.get("id"):
        material = [Material.query.get(request.args.get("id"))]
    else:
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


@api_routes.route('/qrcode/generator')
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
    qrcode = segno.make(content=code_string, micro=False)
    return {"qrcode": qrcode.svg_inline(scale=5), "name": artikel.name}


@api_routes.route("/qrcode/decode", methods=['POST'])
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


@api_routes.route("/material/export", methods=['POST'])
@login_required
def test():
    if request.method != 'POST':
        abort(405)  # Method Not allowed
    if not isinstance(request.json.get('artikel_ids'), list):
        abort(404)
    artikel_ids = request.json.get("artikel_ids")
    try:
        if request.args.get("type") == "pdf":
            generator = PDFGenerator()
            pdf = generator.generate_pdf(Material.query.filter(Material.idMaterial.in_(artikel_ids)).all())
            return send_file(pdf, mimetype="application/pdf")
        else:
            generator = SVGGenerator()
            return generator.generate_svg(Material.query.filter(Material.idMaterial.in_(artikel_ids)).all())
    except ExportError as e:
        return {"success": False, "msg": e.args[0]}

@api_routes.route('/material/checkout', methods=['POST'])
@login_required
def checkout():
    print(request.json)
    if not request.json.get('id'):
        abort(403)
    material: Material = Material.query.get(request.json.get('id'))
    if not material:
        abort(403)
    neue_ausleihe =Ausleihe(
        ersteller_benutzername=current_user.benutzername,
        ts_erstellt=dt.now(),
        ts_von=dt.now(),
        ts_bis=(dt.now() + timedelta(days=1)),
        materialien=material.idMaterial,
        empfaenger=current_user.benutzername,
        beschreibung=f"Per QR-Code")
    db.session.add(neue_ausleihe)
    db.session.commit()
    return Response(status=200)