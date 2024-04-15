from datetime import date
from flask import request, Response, Blueprint
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from sqlalchemy import desc
from werkzeug.utils import redirect
from ..database import db
from ..database.db import (
    Benutzer,
    Rolle,
)

user_site = Blueprint("user_site", __name__, url_prefix="/benutzer")

@user_site.route("/", methods=['GET', 'POST'])
@login_required
def benutzer():
    if request.method == 'POST':
        neuerBenutzer = Benutzer(request.form.get('benutzername'), request.form.get('name'), request.form.get(
            'email'), f"{request.form.get('benutzername')}", Rolle.query.filter_by(name=request.form.get('rolle')).first().idRolle)
        db.session.add(neuerBenutzer)
        db.session.commit()
        return redirect(url_for(".benutzer"))
    else:
        if current_user.Rolle.schreibenBenutzer:
            erlaubeBearbeiten = True
        else:
            erlaubeBearbeiten = False
        liste = Benutzer.query.order_by(Benutzer.name).all()
        rollen = Rolle.query.all()

        return render_template('user/benutzer.html', benutzer_liste=liste, roles=rollen, edit=erlaubeBearbeiten)


@user_site.route('/<benutzername>', methods=['GET', 'POST'])
@login_required
def profil(benutzername):
    error_msg = ""
    if request.method == 'POST':
        if current_user.benutzername == benutzername or current_user.Rolle.schreibenBenutzer:
            # User edits own profile
            user = Benutzer.query.get(benutzername)
            if request.form.get("delete", "off") == 'on':
                # User deletes own profile
                db.session.delete(user)
                db.session.commit()
                return redirect(url_for(".benutzer"))
            else:
                user.benutzername = request.form['benutzername']
                user.name = request.form['name']
                user.email = request.form['email']
                if request.form.get('rolle'):
                    user.rolleRef = Rolle.query.filter_by(
                        name=request.form.get('rolle')).first().idRolle
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
        if current_user.Rolle.lesenBenutzer is False and current_user.benutzername is not benutzername:
            return Response(f'Du hast keinen Zugriff auf das Profil von {benutzername}.', 401)
        user = Benutzer.query.get(benutzername)
        rollen = Rolle.query.all()
        if current_user.Rolle.schreibenBenutzer:
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
