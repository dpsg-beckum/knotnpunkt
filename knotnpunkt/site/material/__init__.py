import base64
import json
from datetime import date
from datetime import datetime as dt
from logging import debug
from pprint import pprint

import humanize as hu
from flask import Blueprint, abort, flash, jsonify, request
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required
from sqlalchemy import desc
from werkzeug.datastructures.file_storage import FileStorage
from werkzeug.utils import redirect

from ...database.material import (Ausleihe, Img, KategorieSpezifisch, Material,
                                  Set)
from ...utils import checkverfuegbarkeit
from .kategorien import kategorie_site
from .materialforms import EditMaterialForm, NewMaterialForm
from .sets import sets_site

material_site = Blueprint("material", __name__, url_prefix="/material")
material_site.register_blueprint(kategorie_site)
material_site.register_blueprint(sets_site)


@material_site.before_request
@login_required
def auth():
    pass


@material_site.route("/new", methods=['GET', 'POST'])
def new_material():

    all_kategorien = KategorieSpezifisch.get_all()

    # return str([k.to_dict() for k in all_kategorien])

    ks: list[dict[str, str | dict]] = []
    for i in [k.to_dict() for k in all_kategorien]:
        print(i)
        kuerzel = f"{i['kategorie_typen']['kuerzel']}{i.get('kuerzel')}"
        data = {
            "id": i.get("id"),
            "name": f"{kuerzel} {i['kategorie_typen']['name']}-{i.get('name')}"
        }
        ks.append(data)

    form = NewMaterialForm()

    form.category.choices = [(k.get("id"), k.get("name")) for k in ks]
    form.set.choices = [(s.id, s.name) for s in Set.get_all()]

    form.update_form()

    print(form.category.choices)

    if form.validate_on_submit():
        kategorie = KategorieSpezifisch.get_via_id(form.category.data)
        title = form.title.data if form.title.data else kategorie.kategorie_typen.name
        Material.create_new(
            name=title,
            kategorie=kategorie,
            description=form.description.data,
            eigenschaften={
                "artNr": form.artNr.data,
            }
        )
        return redirect(url_for(".material"))

    if form.errors:
        flash(f"Fehler beim Speichern des Materials {form.errors}", "danger")
        flash(form.data)

    return render_template('material/new.html', form=form)


@material_site.route("/", methods=['GET', 'POST'])
def index():
    return render_template('material/index.html')


@material_site.get("/overview")
def material():
    materialien = Material.get_all()
    verfuegbarkeit = checkverfuegbarkeit(materialien)
    kategorien = []

    return render_template('material/overview.html',
                           materialien=[m.to_dict() for m in materialien],
                           kategorienListe=kategorien,
                           verfuegbarkeit=verfuegbarkeit,
                           jsonRef=json, huRef=hu, dtRef=dt)


@material_site.route('/<int:id>/show', methods=['GET'])
def show(id):
    print(f"Getting Material with ID {id}")
    mat = Material.get_via_id(id)

    # return str(data)
    materialien = Material.get_all()
    # Hier schon direkt Filtern ob MaterialID(Int) in Ausgeliehenem Material(Str) ist?
    ausleihen = Ausleihe.get_all()  # TODO Sort by ts_von
    ausleihen_filtered_future = []
    ausleihen_filtered_past = []
    # verfuegbarkeit = checkverfuegbarkeit(material_details)
    for a in ausleihen:
        if int(id) in [int(x) for x in a.materialien.split(",") if x.isdigit()]:
            if a.ts_von > date.today():
                ausleihen_filtered_future.append(a)
            else:
                ausleihen_filtered_past.append(a)
    if len(ausleihen_filtered_past):
        zuletzt_ausgeliehen_Tage = (
            date.today() - ausleihen_filtered_past[0].ts_von).days
    else:
        zuletzt_ausgeliehen_Tage = None

    # kategorien = Kategorie.get_all() # TODO implement
    kategorien = []
    material_images = [i.to_dict() for i in Img.filter_by(material_id=id)]

    return render_template('material/show.html',
                           material=mat.to_dict(2),
                           materialListe=materialien,
                           kategorienListe=kategorien,
                           ausleihListeZukunft=ausleihen_filtered_future,
                           ausleihListeAlt=ausleihen_filtered_past,
                           #    verfuegbarkeit=verfuegbarkeit,
                           zuletzt_ausgeliehen_Tage=zuletzt_ausgeliehen_Tage,
                           jsonRef=json, huRef=hu, dtRef=dt,
                           images=material_images)


@material_site.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    material = Material.get_via_id(id)

    form = EditMaterialForm()

    form.delete_images.choices = [(i.id, i.id)
                                  for i in Img.filter_by(material_id=id)]

    ks: list[dict[str, str | dict]] = []
    for i in [k.to_dict() for k in KategorieSpezifisch.get_all()]:
        kuerzel = f"{i['kategorie_typen']['kuerzel']}{i.get('kuerzel')}"
        data = {
            "id": i.get("id"),
            "name": f"{kuerzel} {i['kategorie_typen']['name']}-{i.get('name')}"
        }
        ks.append(data)
    form.category.choices = [(k.get("id"), k.get("name")) for k in ks]
    form.set.choices = [(s.id, s.name) for s in Set.get_all()]

    if form.validate_on_submit():
        print(form.images.data)

        kategorie = KategorieSpezifisch.get_via_id(form.category.data)
        set = Set.get_via_id(form.set.data)
        material.update(
            name=form.title.data,
            description=form.description.data,
            eigenschaften=dict(material.eigenschaften) | {
                "artNr": form.artNr.data}
        )
        material.set_kategorie(kategorie)
        material.add_to_set(set)

        if form.images.data:

            image: FileStorage
            for image in form.images.data:
                print(image)
                print(type(image))
                Img.create_new(
                    material=material,
                    img=image.stream.read(),
                    mimetype=image.mimetype
                )
        return redirect(url_for(".material"))

    if form.errors:
        flash(
            f"Fehler beim Speichern des Materials {form.errors}", "danger")

    form.title.data = material.name
    # materialForm.category.data = "SE Seitenbahn-Einzel"
    form.category.data = material.spezifisch_id
    form.description.data = material.description
    form.artNr.data = material.eigenschaften.get("artNr", "")
    form.set.data = material.set_id
    form.update_form()

    return render_template('material/edit.html',
                           material=material.to_dict(),
                           materialForm=form)


@material_site.route('/reservieren/<idMaterial>', methods=['POST'])
def materialReservieren(idMaterial):
    debug(request.form.get('reservierte_Materialien'))

    Ausleihe.create_new(ersteller=current_user,
                        empfaenger=request.form.get('empfaenger') if request.form.get(
                            'empfaenger') else current_user.benutzername,
                        ts_von=dt.strptime(request.form.get(
                            'reservieren_von'), "%Y-%m-%d"),
                        ts_bis=dt.strptime(request.form.get(
                            'reservieren_bis'), "%Y-%m-%d"),
                        beschreibung=request.form.get('beschreibung'),
                        materialien=request.form.get('reservierte_Materialien')
                        )

    return redirect(url_for(".material"))


@material_site.route('/img/upload/<idMaterial>', methods=['POST'])
def upload_img(idMaterial):
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    material = Material.get_via_id(idMaterial)
    mimetype = pic.mimetype
    if not mimetype:
        return 'Bad upload!', 400
    Img.create_new(
        material=material,
        img=pic.read(),
        mimetype=mimetype
    )
    return redirect(url_for(".show", idMaterial=idMaterial))


@material_site.route('/img/delete/<id>/<idMaterial>')  # , methods=['POST']
def delete_img(id, idMaterial):
    Img.get_via_id(id)  # TODO Delete Image from Database
    return redirect(url_for(".show", idMaterial=idMaterial))


@material_site.route('/scanner')
def scanner():
    return render_template('material/scanner.html')


@material_site.route("/kalender")
def kalender():
    return render_template('material/kalender.html')
