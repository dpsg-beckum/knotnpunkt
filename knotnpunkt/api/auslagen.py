"""This contains the API.ROutes for the Auslagen feature.
"""
import logging
import json
from datetime import datetime as dt
from flask import (
    Blueprint,
    request,
    abort,
    send_file,
)
from flask_login import login_required, current_user
from ..database import db
from ..database.json_encoder import DatabaseEncoder
from ..database.db import (
    Auslage,
    AuslagenBild,
)
from ..utils import (
    allowed_file,
)
from .._version import __version__
from ..export.file_generators import (
    ExportError,
    AuslagenSVGGenerator,
    AuslagenPDFGenerator,
)

logger = logging.getLogger("knotnpunkt")

auslagen_routes = Blueprint("auslagen_routes", __name__, template_folder="templates",
                url_prefix="/auslagen")

@auslagen_routes.get("/")
@login_required
def get_zahlungen():
    """Get all Auslagen a user has read access for. On the home page this is
    called with the onlyAuthored parameter.
    """
    data = {"request": request.args, "response": []}
    data['user'] = json.dumps(current_user, cls=DatabaseEncoder)
    if current_user.Rolle.lesenAlleAuslagen is True and not request.args.get("onlyAuthored", False):
        data['response'] = [ausl.to_dict() for ausl in Auslage.query.all()]
    else:
        data['response'] = [ausl.to_dict() for ausl in current_user.Auslagen]
    return data


@auslagen_routes.post("/")
@login_required
def post_zahlungen():
    """Create a new Auslage from form input posted with JavaScript
    """
    file = request.files.get('belegbild', False)
    if not file or file.filename == "" or not allowed_file(file.filename):
        logger.info("No File")
        abort(422)
    # Test if all the required data was received
    for elem in ["titel", "betrag", "iban", "kontoinhaber", "kategorieId"]:
        if not request.form.get(elem, False):
            logger.debug(f"{elem} is missing")
            return f"{elem} is missing", 422
    new_auslage = Auslage(
        titel=request.form.get("titel"),
        betrag=request.form.get("betrag"),
        iban=request.form.get("iban"),
        bic=request.form.get("bic"),
        kontoinhaber=request.form.get("kontoinhaber"),
        grund=request.form.get("grund"),
        kategorieId=request.form.get("kategorieId"),
        eingereicht_zeit=dt.now(),
        erstellerBenutzername=current_user.benutzername
    )
    # Update users iban
    current_user.iban = request.form.get("iban")
    db.session.add(current_user)
    db.session.add(new_auslage)
    db.session.commit()
    # Sore IMage in Database - TODO: File compression?
    new_AulsImg = AuslagenBild(img=file.read(), Auslage_id=new_auslage.idAuslage, mimetype=file.mimetype)
    db.session.add(new_AulsImg)
    db.session.commit()
    return {"success": True, "auslage": new_auslage.to_dict()}


@auslagen_routes.delete("/<id>")
@login_required
def delete_auslage(id):
    """Delete a Auslage by sending a http-DELETE Request

    Args:
        id (int): Primary key of the Auslage
    """
    auslage: Auslage = Auslage.query.get(id)
    if not auslage:
        abort(404)
    if auslage.Bild is not []:
        db.session.delete(auslage.Bild[0])
    db.session.delete(auslage)
    db.session.commit()
    return auslage.to_dict()


@auslagen_routes.patch("/<id>")
@login_required
def patch_auslagen(id):
    """Accept a Auslage

    Args:
        id (int): Primary Key fo the Auslage
    """
    action: str = request.args.get("action")
    auslage: Auslage = Auslage.query.get(id)
    if not auslage or not action:
        abort(404)
    elif action == "freigabe":
        # User needs respective permission and mustn't accept his own Auslagen
        if not current_user.Rolle.freigebenAuslagen or current_user == auslage.Ersteller:
            abort(403)
        # In the end a PATCH-call toggles from unaccepted to accepted and vice versa
        if auslage.Freigebende is None:
            auslage.freigabe_zeit = dt.now()
            auslage.Freigebende = current_user
        else:
            auslage.freigabe_zeit = None
            auslage.Freigebende = None
        db.session.add(auslage)
        db.session.commit()
        return auslage.to_dict()
    elif action == "done":
        if not current_user.Rolle.lesenAlleAuslagen:
            abort(403)
        if auslage.ErledigtDurch is None:
            auslage.erledigtZeit = dt.now()
            auslage.ErledigtDurch = current_user
            db.session.add(auslage)
            db.session.commit()
        return auslage.to_dict()
    else:
        abort(501)


@auslagen_routes.get("/export")
def export_auslage():
    """Returns SVG code or a PDF file with the rendered template. Called by
    clicking the printer Symbol
    """
    auslage: Auslage = Auslage.query.get(request.args.get('id'))
    if not auslage:
        abort(404)
    try:
        if request.args.get("type") == "pdf":
            generator = AuslagenPDFGenerator()
            pdf = generator.generate_pdf(auslage, 2)
            return send_file(pdf, mimetype="application/pdf", as_attachment=False,  download_name=f"auslage_{auslage.idAuslage}_{auslage.kontoinhaber.replace(' ', '_')}")
        else:
            generator = AuslagenSVGGenerator()
            return generator.generate_svg(auslage, 2)
    except ExportError as e:
        return {"success": False, "msg": e.args[0]}
