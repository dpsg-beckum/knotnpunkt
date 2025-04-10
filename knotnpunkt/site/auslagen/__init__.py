import base64
import json
from datetime import date
from datetime import datetime as dt
from logging import debug
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

from ...database.auslagen import Auslage, AuslagenBild, AuslagenKategorie
from ...database.db import Benutzer, Rolle
from ...database.exceptions import ElementNotEditable
from ...export.file_generators import (AuslagenPDFGenerator,
                                       AuslagenSVGGenerator, ExportError)
from .forms import EditAuslagenForm, NewAuslagenForm

auslagen_site = Blueprint("auslagen", __name__, url_prefix="/auslagen")


@auslagen_site.before_request
@login_required
def auth():
    pass


@auslagen_site.get("/")
def index():
    usr: Benutzer = current_user
    if not (usr.Rolle.lesenAlleAuslagen or usr.Rolle.freigebenAuslagen):
        return redirect(url_for(".deine"))
    return redirect(url_for(".deine"))
    return render_template("auslagen/index.html")


@auslagen_site.route("/deine", methods=["GET", "POST"])
def deine():
    usr: Benutzer = current_user
    auslagen = Auslage.filter_by(ersteller_id=usr.benutzername)
    return render_template("auslagen/deine.html", auslagen=[a.to_dict() for a in auslagen])


@auslagen_site.route("/<int:id>",  methods=["GET", "POST"])
def show(id):
    usr: Benutzer = current_user
    auslage = Auslage.get_via_id(id)

    form = EditAuslagenForm()

    form.category.choices = [(k.id,
                              f"{k.anzeigeName}" + (" (aktuell)" if k.id == auslage.Kategorie.id else ""))
                             for k in AuslagenKategorie.get_all()]

    if form.validate_on_submit():
        if form.delete.data:
            try:
                auslage.delete()
            except Exception as e:
                debug(f"Fehler beim Löschen der Auslage: {e}")
                flash("Fehler beim Löschen der Auslage", "danger")
                return redirect(url_for(".show", id=auslage.id))
            flash(f"Auslage {auslage.id} gelöscht", "success")
            return redirect(url_for(".deine"))

        if form.approve.data:
            try:
                auslage.freigeben(usr)
            except ValueError as e:
                flash(
                    f"Fehler: {e}", "danger")

        if form.done.data:
            try:
                auslage.erledigen(usr)
            except ValueError as e:
                flash(f"Fehler: {e}", "danger")

        if form.submit.data:
            try:
                auslage.update(
                    titel=form.title.data,
                    kategorie_id=AuslagenKategorie.get_via_id(
                        form.category.data).id,
                    comment=form.comment.data
                )
            except ElementNotEditable as e:
                flash(f"Fehler: {e}", "danger")

        return redirect(url_for(".show", id=auslage.id))

    form.category.data = auslage.Kategorie.id
    form.title.data = auslage.titel
    form.comment.data = auslage.grund

    form.update_form()
    return render_template("auslagen/show.html", auslage=auslage.to_dict(), user=usr.to_dict(), form=form)


@auslagen_site.get("/<int:id>/print")
def print(id):
    auslage: Auslage = Auslage.get_via_id(id)
    if not auslage:
        abort(404)
    try:
        if request.args.get("type") == "svg":
            generator = AuslagenSVGGenerator()
            return generator.generate_svg(auslage, 2)
        else:
            generator = AuslagenPDFGenerator()
            pdf = generator.generate_pdf(auslage, 2)
            return send_file(pdf, mimetype="application/pdf", as_attachment=False,  download_name=f"auslage_{auslage.id}_{auslage.kontoinhaber.replace(' ', '_')}")
    except ExportError as e:
        return {"success": False, "msg": e.args[0]}


@auslagen_site.route("/new", methods=["GET", "POST"])
def new():
    usr: Benutzer = current_user

    kategorie = AuslagenKategorie.get_all()

    form = NewAuslagenForm()

    form.category.choices = [(k.id, k.anzeigeName) for k in kategorie]

    if form.validate_on_submit():
        # Bild speichern
        bild: FileStorage = form.image.data
        if not bild:
            abort(400, "Kein Bild hochgeladen")

        auslage = Auslage.create_new(
            titel=form.title.data,
            betrag=form.betrag.data,
            iban=form.iban.data,
            bic=form.bic.data,
            kontoinhaber=form.kontoinhaber.data,
            grund=form.comment.data,
            eingereicht_zeit=dt.now(),
            erstellerBenutzername=usr.benutzername,
            kategorie=AuslagenKategorie.get_via_id(form.category.data),
        )

        AuslagenBild.create_new(
            auslage=auslage,
            img=base64.b64encode(bild.read()),
            mimetype=bild.mimetype,
        )

        flash("Auslage erfolgreich eingereicht", "success")
        return redirect(url_for(".deine"))

    auslagen = Auslage.filter_by(ersteller_id=usr.benutzername)

    if auslagen:
        form.kontoinhaber.data = auslagen[-1].kontoinhaber
        form.iban.data = auslagen[-1].iban
        form.bic.data = auslagen[-1].bic

    form.update_form()

    return render_template("auslagen/new.html", form=form)
