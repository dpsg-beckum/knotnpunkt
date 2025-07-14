import base64
import json
from collections import Counter
from datetime import date
from datetime import datetime as dt
from logging import debug
from pprint import pprint
from typing import List

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
                                  KategorieTypen, Material, Set, SetTypes)
from ...utils import checkverfuegbarkeit
from .setforms import NewSetForm, NewSetTypeForm

sets_site = Blueprint("sets", __name__, url_prefix="/sets")


@sets_site.before_request
@login_required
def auth():
    pass


@sets_site.get("/")
def index():
    return redirect(url_for('.overview'))


@sets_site.route("/overview", methods=['GET', 'POST'])
def overview():
    sets = Set.get_all()

    for s in sets:
        ctr = Counter()
        set_kuerzel = s.setType.kuerzel
        for m in s.materials:
            kat = m.spezifisch.kategorie_typen
            key = (
                set_kuerzel,
                kat.kuerzel,
                m.spezifisch.name,
                kat.name
            )
            ctr[key] += 1

        # Use setattr to add 'groups' dynamically
        setattr(s, 'groups', [
            {
                'count': cnt,
                'set_kuerzel': k[0],
                'kat_kuerzel': k[1],
                'spez_name':   k[2],
                'kat_name':    k[3],
            }
            for k, cnt in ctr.items()
        ])

    # Now to_dict will include 'groups' because of your improved implementation
    sets_dicts = [s.to_dict() for s in sets]

    return render_template("material/sets/overview.html", sets=sets_dicts)


@sets_site.route("/new", methods=['GET', 'POST'])
def new():
    form = NewSetForm()

    if form.validate_on_submit():
        try:
            Set.create_new(
                number=form.number.data,
                setType=form.set_type.data
            )
            flash("Set erfolgreich erstellt", "success")
            return redirect(url_for(".index"))
        except ElementAlreadyExists as e:
            flash(e, "danger")

    return render_template("material/sets/new.html", form=form)


# def setType_new():
#     form = NewSetTypeForm()

#     if form.validate_on_submit():
#         try:
#             SetTypes.create_new(
#                 name=form.name.data,
#                 kuerzel=form.kuerzel.data
#             )
#             flash("SetTyp erfolgreich erstellt", "success")
#             return redirect(url_for(".show"))
#         except ElementAlreadyExists as e:
#             flash(e, "danger")

#     return render_template("material/sets/setType_new.html", form=form)


@sets_site.route("/<int:id>", methods=['GET', 'POST'])
def show(id):

    set = Set.get_via_id(id)

    groups: List[dict[KategorieSpezifisch, List[Material]]] = []
    kategorien: dict[KategorieSpezifisch, List[Material]] = {}
    for m in set.materials:
        key = m.spezifisch
        if key not in kategorien:
            kategorien[key] = []
        kategorien[key].append(m)
    for k, mats in kategorien.items():
        mats.sort(key=lambda x: x.numberinset if x.numberinset else x.name)
        data = {
            "kategorie": k.to_dict(0),
            "materials": [m.to_dict(0) for m in mats],
        }
        groups.append(data)

    setattr(set, 'groups', groups)

    return render_template("material/sets/show.html", set=set.to_dict())


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
