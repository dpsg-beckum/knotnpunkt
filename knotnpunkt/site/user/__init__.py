from datetime import date

from flask import Blueprint, Response, request
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from sqlalchemy import desc
from werkzeug.utils import redirect

from ...database.db import Benutzer, Rolle
from .forms import ChangePasswordForm, EditProfileForm, InitalLoginForm

user_site = Blueprint("user", __name__, url_prefix="/benutzer")


@user_site.before_request
@login_required
def auth():
    pass


@user_site.route("/inital_login", methods=['GET', 'POST'])
def inital_login():
    usr: Benutzer = current_user
    form: InitalLoginForm = InitalLoginForm()

    if form.validate_on_submit():
        if form.passwort.data == form.passwortBestaetigung.data:
            usr.set_passwort(form.passwort.data)
            usr.update(
                name=form.name.data,
                emailAdresse=form.email.data,
            )
            return redirect(url_for("site.index"))

    form.name.data = usr.name if usr.name else ""
    form.email.data = usr.emailAdresse if usr.emailAdresse else ""
    form.strasse.data = usr.strasse if usr.strasse else ""
    form.hausnummer.data = usr.hausnummer if usr.hausnummer else ""
    form.plz.data = usr.postleitzahl if usr.postleitzahl else ""
    form.ort.data = usr.ort if usr.ort else ""
    form.iban.data = usr.iban if usr.iban else ""

    return render_template('user/intital_login.html', form=form, user=usr.to_dict())


@user_site.get('/')
def profil():
    usr: Benutzer = current_user
    return render_template('user/profil.html', user=usr.to_dict())


@user_site.route('/change_password', methods=['GET', 'POST'])
def change_password():
    usr: Benutzer = current_user
    form: ChangePasswordForm = ChangePasswordForm()

    if form.validate_on_submit():
        if form.passwort.data == form.passwortBestaetigung.data:
            usr.set_passwort(form.passwort.data)
            return redirect(url_for("site.logout"))
    return render_template('user/change_password.html', form=form, user=usr.to_dict())


@user_site.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    usr: Benutzer = current_user
    form: EditProfileForm = EditProfileForm()

    if form.validate_on_submit():
        usr.update(
            name=form.name.data,
            emailAdresse=form.email.data,
            strasse=form.strasse.data,
            hausnummer=form.hausnummer.data,
            postleitzahl=form.plz.data,
            ort=form.ort.data,
            iban=form.iban.data
        )
        return redirect(url_for(".profil"))

    form.name.data = usr.name
    form.email.data = usr.emailAdresse
    form.strasse.data = usr.strasse if usr.strasse else ""
    form.hausnummer.data = usr.hausnummer if usr.hausnummer else ""
    form.plz.data = usr.postleitzahl if usr.postleitzahl else ""
    form.ort.data = usr.ort if usr.ort else ""
    form.iban.data = usr.iban if usr.iban else ""

    return render_template('user/edit.html', form=form, user=usr.to_dict())
