from datetime import datetime as dt
from datetime import date
from flask import request, Blueprint
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required
from sqlalchemy import desc
from werkzeug.utils import redirect
from logging import debug
import json
import base64
import humanize as hu
from ..database import db
from ..database.db import (
    Material,
    Kategorie,
    Ausleihe,
    Img,
)
from ..utils import checkverfuegbarkeit

material_site = Blueprint("material_site", __name__, url_prefix="/material")


@material_site.route("/", methods=['GET', 'POST'])
@login_required
def material():
    if request.method == 'POST':
        eigenschaften = {"anzahl": int(request.form.get('anzahl'))}
        if request.form.get('beschreibung'):
            eigenschaften['beschreibung'] = request.form.get('beschreibung')
        if request.form.get('rhArtNummer'):
            eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
        if request.form.get('verpackung'):
            eigenschaften['verpackung'] = request.form.get('verpackung')
        if int(eigenschaften['anzahl']) > 1:
            eigenschaften['verfuegbar'] = 1
        eigenschaften['zuletztGescannt'] = dt.strftime(
            dt.now(), "%Y-%m-%d %H:%M")
        neuesMaterial = Material(request.form.get(
            'name'), request.form.get('kategorie'), eigenschaften)
        db.session.add(neuesMaterial)
        db.session.commit()
        return redirect(url_for(".material"))
    else:
        materialien = Material.query.all()
        verfuegbarkeit = checkverfuegbarkeit(materialien)
        kategorien = Kategorie.query.all()
        material_list = []
        for material in materialien:
            id = material.idMaterial
            image = Img.query.filter_by(Material_idMaterial=id).first()
            if image != None:
                material_list.append(
                    [material, base64.b64encode(image.img).decode('utf-8')])
            else:
                material_list.append([material, None])
        return render_template('material/material.html', materialListe=material_list, kategorienListe=kategorien, verfuegbarkeit=verfuegbarkeit,  jsonRef=json, huRef=hu, dtRef=dt)


@material_site.route('/<idMaterial>', methods=['GET'])
@login_required
def materialDetails(idMaterial):
    material_details = Material.query.filter_by(idMaterial=idMaterial).all()
    materialien = Material.query.all()
    # Hier schon direkt Filtern ob MaterialID(Int) in Ausgeliehenem Material(Str) ist?
    ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_von)).all()
    ausleihen_filtered_future = []
    ausleihen_filtered_past = []
    verfuegbarkeit = checkverfuegbarkeit(material_details)
    for a in ausleihen:
        if int(idMaterial) in [int(x) for x in a.materialien.split(",") if x.isdigit()]:
            if a.ts_von > date.today():
                ausleihen_filtered_future.append(a)
            else:
                ausleihen_filtered_past.append(a)
    if len(ausleihen_filtered_past):
        zuletzt_ausgeliehen_Tage = (
            date.today() - ausleihen_filtered_past[0].ts_von).days
    else:
        zuletzt_ausgeliehen_Tage = None
    kategorien = Kategorie.query.all()
    material_images = Img.query.filter_by(Material_idMaterial=idMaterial).all()
    img_id_list = []
    if material_images:
        for image in material_images:
            img_id_list.append(
                [image.img_id, base64.b64encode(image.img).decode('utf-8')])
    else:
        img_id_list.append(None)
    return render_template('material/material_details.html', material_details=material_details, materialListe=materialien, kategorienListe=kategorien, ausleihListeZukunft=ausleihen_filtered_future, ausleihListeAlt=ausleihen_filtered_past, verfuegbarkeit=verfuegbarkeit, zuletzt_ausgeliehen_Tage=zuletzt_ausgeliehen_Tage, jsonRef=json, huRef=hu, dtRef=dt, images=img_id_list)


@material_site.route('/edit/<idMaterial>', methods=['POST'])
@login_required
def materialDetailsEdit(idMaterial):
    material_update = Material.query.filter_by(idMaterial=idMaterial).first()
    material_update.name = request.form.get('name')
    material_update.Kategorie_idKategorie = request.form.get('kategorie')
    eigenschaften = dict(material_update.Eigenschaften)
    debug(eigenschaften)
    debug(f"{request.form.get('beschreibung')},{request.form.get('rhArtNummer')},{request.form.get('verpackung')}")
    if request.form.get('beschreibung'):
        eigenschaften['beschreibung'] = request.form.get('beschreibung')
    if request.form.get('rhArtNummer'):
        eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
    if request.form.get('verpackung'):
        eigenschaften['verpackung'] = request.form.get('verpackung')
    if request.form.get('anzahl'):
        if int(request.form.get('anzahl')) > 1:
            eigenschaften['anzahl'] = int(request.form.get('anzahl'))
            eigenschaften['zaehlbar'] = True
        else:
            eigenschaften['zaehlbar'] = False
    material_update.Eigenschaften = eigenschaften
    debug(eigenschaften)
    debug(material_update.Eigenschaften)
    db.session.commit()
    return redirect(url_for(".materialDetails", idMaterial=idMaterial))


@material_site.route('/reservieren/<idMaterial>', methods=['POST'])
@login_required
def materialReservieren(idMaterial):
    debug(request.form.get('reservierte_Materialien'))
    neueReservierung = Ausleihe(
        ersteller_benutzername=current_user.benutzername,
        ts_erstellt=dt.now(),
        ts_von=dt.strptime(request.form.get('reservieren_von'), "%Y-%m-%d"),
        ts_bis=dt.strptime(request.form.get('reservieren_bis'), "%Y-%m-%d"),
        materialien=request.form.get('reservierte_Materialien'),
        empfaenger=request.form.get('empfaenger') if request.form.get(
            'empfaenger') else current_user.benutzername,
        beschreibung=request.form.get('beschreibung'))
    db.session.add(neueReservierung)
    db.session.commit()
    return redirect(url_for(".material"))


@material_site.route('/img/upload/<idMaterial>', methods=['POST'])
@login_required
def upload_img(idMaterial):
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400
    material_id = idMaterial
    mimetype = pic.mimetype
    if not material_id or not mimetype:
        return 'Bad upload!', 400
    img = Img(img=pic.read(), Material_idMaterial=material_id, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()
    return redirect(url_for(".materialDetails", idMaterial=idMaterial))


@material_site.route('/img/delete/<id>/<idMaterial>')  # , methods=['POST']
@login_required
def delete_img(id, idMaterial):
    Img.query.filter_by(img_id=id).delete()
    db.session.commit()
    return redirect(url_for(".materialDetails", idMaterial=idMaterial))


@material_site.route('/scanner')
@login_required
def scanner():
    return render_template('material/scanner.html')


@material_site.route('/qrcode-generator', methods=['GET'])
@login_required
def qrcode_generator():
    materialien = Material.query.all()
    kategorien = Kategorie.query.all()
    return render_template('material/qrgenerator.html', materialListe=materialien, kategorienListe=kategorien)
