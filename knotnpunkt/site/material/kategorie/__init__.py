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

from ....database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from ....database.material import (Ausleihe, Img, KategorieSpezifisch,
                                   KategorieTypen, Material, Set)
from ....utils import checkverfuegbarkeit
from ..materialforms import EditMaterialForm, NewMaterialForm
from ..sets import sets_site
from .kategorienforms import NewKategorieStep1Form, NewKategorieStep2Form

kategorie_material_site = Blueprint(
    "kategorie", __name__, url_prefix="/kategorie")


@kategorie_material_site.route("/", methods=['GET', 'POST'])
def index():

    form = NewKategorieStep1Form()

    if form.validate_on_submit():
        try:
            KategorieTypen.create_new(
                name=form.name.data,
                kuerzel=form.kuerzel.data
            )
            flash("Kategorie erfolgreich erstellt", "success")
            return redirect(url_for(".index"))
        except ElementAlreadyExists as e:
            flash(e, "danger")

    return render_template("material/kategorie/index.html",
                           form=form,
                           kategorien=[k.to_dict()
                                       for k in KategorieTypen.get_all()],
                           material=[m.to_dict(3) for m in Material.get_all()]
                           )


@kategorie_material_site.route("/<int:id>", methods=['GET', 'POST'])
def category(id):

    kategorie = KategorieTypen.get_via_id(id)
    subkategorien = KategorieSpezifisch.filter_by(
        kategorie_typen_id=kategorie.id)

    form = NewKategorieStep2Form()

    if form.validate_on_submit():
        try:
            KategorieSpezifisch.create_new(
                name=form.name.data,
                kuerzel=form.kuerzel.data,
                typ=kategorie
            )
            flash("Subkategorie erfolgreich erstellt", "success")
            return redirect(url_for(".category", id=kategorie.id))
        except ElementAlreadyExists as e:
            flash(e, "danger")

    return render_template("material/kategorie/category.html",
                           form=form,
                           kategorie=kategorie.to_dict(3),
                           subkategorien=[k.to_dict() for k in subkategorien],
                           material=[
                               m.to_dict(3) for s in subkategorien for m in s.material]
                           )


@kategorie_material_site.route("/sub/<int:id>/", methods=['GET', 'POST'])
def subcategory(id):
    subkategorie = KategorieSpezifisch.get_via_id(id)
    return render_template("material/kategorie/subcategory.html",
                           kategorie=subkategorie.kategorie_typen.to_dict(3),
                           subkategorie=subkategorie.to_dict(3),
                           material=[m.to_dict(3)
                                     for m in subkategorie.material]
                           )
