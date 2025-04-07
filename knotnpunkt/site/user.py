from datetime import date

from flask import Blueprint, Response, request
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from sqlalchemy import desc
from werkzeug.utils import redirect

from ..database import db
from ..database.db import Benutzer, Rolle

user_site = Blueprint("user_site", __name__, url_prefix="/benutzer")


@user_site.route("/", methods=['GET', 'POST'])
@login_required
def benutzer():
    usr: Benutzer = current_user
    if request.method == 'POST':
        neuerBenutzer = Benutzer(request.form.get('benutzername'), request.form.get('name'), request.form.get(
            'email'), f"{request.form.get('benutzername')}", Rolle.get_via_name(name=request.form.get('rolle')).id)
        db.session.add(neuerBenutzer)
        db.session.commit()
        return redirect(url_for(".benutzer"))
    else:
        if usr.Rolle.schreibenBenutzer:
            erlaubeBearbeiten = True
        else:
            erlaubeBearbeiten = False
        liste = Benutzer.get_all()
        rollen = Rolle.get_all()

        return render_template('user/benutzer.html', benutzer_liste=liste, roles=rollen, edit=erlaubeBearbeiten)


@user_site.route('/<benutzername>', methods=['GET', 'POST'])
@login_required
def profil(benutzername):
    usr: Benutzer = current_user
    error_msg = ""
    if request.method == 'POST':
        if usr.benutzername == benutzername or usr.Rolle.schreibenBenutzer:
            # User edits own profile
            user = Benutzer.get_via_id(benutzername)
            if request.form.get("delete", "off") == 'on':
                # User deletes own profile
                db.session.delete(user)
                db.session.commit()
                return redirect(url_for(".benutzer"))
            else:
                user.benutzername = request.form['benutzername']
                user.name = request.form['name']
                user.emailAdresse = request.form['email']
                if request.form.get('rolle'):
                    user.rolle_id = Rolle.get_via_name(
                        request.form.get('rolle')).id
                if request.form.get('passwort'):
                    if request.form.get('passwort') == request.form.get('passwortBestaetigung'):
                        user.set_passwort(request.form.get('passwort'))
                        db.session.add(user)
                        db.session.commit()
                        logout_user()
                        return redirect(url_for("site.login", newPassword=True))
                    else:
                        error_msg = "Änderung fehlgeschlagen. Bitte bestätige dein Passwort."
                        return redirect(url_for(".profil", benutzername=benutzername, missingPwdConfirm=True))
                db.session.add(user)
                db.session.commit()
                return redirect(url_for(".benutzer"))
    elif request.method == 'GET':
        if usr.Rolle.lesenBenutzer is False and usr.benutzername is not benutzername:
            return Response(f'Du hast keinen Zugriff auf das Profil von {benutzername}.', 401)
        user = Benutzer.get_via_id(benutzername)
        rollen = Rolle.get_all()
        if usr.Rolle.schreibenBenutzer:
            edit_permission = True
        else:
            edit_permission = False
        hide_menu = False
        if request.args.get("initialLogin"):
            error_msg = "Vergib ein eigenes Passwort, um dein Konto zu aktivieren."
            hide_menu = True
        elif request.args.get('missingPwdConfirm'):
            error_msg = "Bitte bestätige das neues Passwort."
        return render_template('user/profil.html', user=user, roles=rollen, edit=edit_permission, hide_menu=hide_menu, error=error_msg)
