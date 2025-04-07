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

from ...database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from ...database.material import (Ausleihe, Img, KategorieSpezifisch,
                                  KategorieTypen, Material, Set)
from ...utils import checkverfuegbarkeit
from .kategorienforms import NewKategorieStep1Form, NewKategorieStep2Form

kategorie_site = Blueprint("kategorie", __name__, url_prefix="/kategorie")


@kategorie_site.before_request
@login_required
def auth():
    pass


@kategorie_site.route("/", methods=['GET', 'POST'])
def show():
    kat = KategorieTypen.get_all()
    return render_template("material/kategorie/step1.html", kategorien=[k.to_dict() for k in kat])


@kategorie_site.route("/new", methods=['GET', 'POST'])
def step1_new():
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

    return render_template("material/kategorie/step1_new.html", form=form)


@kategorie_site.route("/<int:id>", methods=['GET', 'POST'])
def step1_show(id):

    step1 = KategorieTypen.get_via_id(id)

    return render_template("material/kategorie/step1_show.html", kategorie=step1.to_dict(3))


@kategorie_site.route("/<int:id>/new", methods=['GET', 'POST'])
def step2_new(id):

    step1 = KategorieTypen.get_via_id(id)

    form = NewKategorieStep2Form()

    if form.validate_on_submit():
        try:
            KategorieSpezifisch.create_new(
                name=form.name.data,
                kuerzel=form.kuerzel.data,
                typ=step1
            )
            flash("Kategorie erfolgreich erstellt", "success")
            return redirect(url_for(".show"))
        except ElementAlreadyExists as e:
            flash(e, "danger")

    return render_template("material/kategorie/step2_new.html", form=form, kategorie=step1.to_dict())
