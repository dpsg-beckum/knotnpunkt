import base64
import json
import secrets
from datetime import date
from datetime import datetime as dt
from logging import debug
from os import environ
from pprint import pprint

import humanize as hu
from flask import Blueprint, abort, flash, jsonify, request, send_file
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required
from sqlalchemy import desc
from werkzeug.datastructures.file_storage import FileStorage
from werkzeug.utils import redirect

from ...database.db import Benutzer, Rolle
from ...database.exceptions import ElementAlreadyExists, ElementNotEditable
from ...export.file_generators import (AuslagenPDFGenerator,
                                       AuslagenSVGGenerator, ExportError)
from .forms import CreateUserForm, EditUserForm

admin_site = Blueprint("admin", __name__, url_prefix="/admin")


@admin_site.before_request
@login_required
def auth():
    usr: Benutzer = current_user
    if not usr.Rolle.lesenBenutzer:
        abort(403)


@admin_site.get("/")
def index():
    return redirect(url_for(".users"))


@admin_site.get("/benutzer")
def users():
    usrs = [u.to_dict() for u in Benutzer.get_all()]
    return render_template("admin/users.html", users=usrs)


@admin_site.route("/<benutzername>",  methods=["GET", "POST"])
def show(benutzername):
    usr: Benutzer = current_user
    return render_template("admin/show.html", user=benutzername)


@admin_site.route("/<benutzername>/edit",  methods=["GET", "POST"])
def edit(benutzername):
    user = Benutzer.get_via_id(benutzername)
    form = EditUserForm()
    form.rolle.choices = [(r.id, r.name + (" (Aktuell)" if r.id ==
                           user.rolle_id else "")) for r in Rolle.get_all()]

    if form.validate_on_submit():
        try:
            if form.submit.data:
                name = form.name.data
                email = form.email.data
                rolle = Rolle.get_via_id(form.rolle.data)

                user.update(
                    name=name,
                    emailAdresse=email,
                    rolle=rolle,
                )
                flash(
                    f"Benutzer {user.benutzername} erfolgreich bearbeitet.", "success")
                return redirect(url_for(".index"))
            elif form.reset.data:
                passwort = user.reset_passwort()
                flash(
                    f"Passwort für {user.benutzername} zurückgesetzt. {passwort}", "success")
                return redirect(url_for(".index"))
        except ElementNotEditable as e:
            flash(str(e), "error")

    form.name.data = user.name
    form.email.data = user.emailAdresse
    form.rolle.data = user.Rolle.id

    return render_template("admin/edit.html", form=form, user=user.to_dict())


@admin_site.route("/neu", methods=["GET", "POST"])
def new():
    form = CreateUserForm()
    form.rolle_id.choices = [(r.id, r.name) for r in Rolle.get_all()]

    if form.validate_on_submit():
        try:
            if form.passwort.data:
                passwort = form.passwort.data
            else:
                passwort = secrets.token_urlsafe(8)

            benutzer = Benutzer.create_new(
                form.benutzername.data,
                form.name.data,
                form.email.data,
                form.passwort.data,
                Rolle.get_via_id(form.rolle_id.data),
            )
            flash(
                f"Benutzer {benutzer.benutzername} erfolgreich erstellt.\n Password: {passwort}", "success")
            return redirect(url_for(".index"))
        except ElementAlreadyExists as e:
            flash(str(e), "error")

    return render_template("admin/new.html", form=form)
