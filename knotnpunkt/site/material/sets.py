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
from ...database.material import Ausleihe, Img, Material, Set, SetTypes
from ...utils import checkverfuegbarkeit
from .setforms import NewSetForm, NewSetTypeForm

sets_site = Blueprint("sets", __name__, url_prefix="/settype")


@sets_site.before_request
@login_required
def auth():
    pass


@sets_site.route("/", methods=['GET', 'POST'])
def show():
    sets = SetTypes.get_all()
    return render_template("material/sets/setType.html", sets=[s.to_dict() for s in sets])


@sets_site.route("/new", methods=['GET', 'POST'])
def setType_new():
    form = NewSetTypeForm()

    if form.validate_on_submit():
        try:
            SetTypes.create_new(
                name=form.name.data,
                kuerzel=form.kuerzel.data
            )
            flash("SetTyp erfolgreich erstellt", "success")
            return redirect(url_for(".show"))
        except ElementAlreadyExists as e:
            flash(e, "danger")

    return render_template("material/sets/setType_new.html", form=form)


@sets_site.route("/<int:id>", methods=['GET', 'POST'])
def setType_show(id):

    sets = SetTypes.get_via_id(id)

    return render_template("material/sets/setType_show.html", sets=sets.to_dict(3))


@sets_site.route("/<int:id>/new", methods=['GET', 'POST'])
def set_new(id):

    step1 = SetTypes.get_via_id(id)

    form = NewSetForm()

    if form.validate_on_submit():
        try:
            Set.create_new(
                number=form.number.data,
                setType=step1
            )
            flash("Set erfolgreich erstellt", "success")
            return redirect(url_for(".show"))
        except ElementAlreadyExists as e:
            flash(e, "danger")

    return render_template("material/sets/set_new.html", form=form, set=step1.to_dict())
