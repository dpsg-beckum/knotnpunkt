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
    Material,
    Kategorie,
    Ausleihe,
    AuslagenKategorie,
)
from .material import material_site

site = Blueprint("site", __name__, template_folder="templates")
site.register_blueprint(material_site)


@site.route('/')
def redirectToLogin():
    return redirect(url_for('site.login'))


@site.route("/login", methods=['GET', 'POST'])
def login():
    error_msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('site.home'))
    if request.args.get("newPassword"):
        error_msg = "Bitte melde dich mit deinem neuen Passwort an."
    if request.method == 'POST':
        user = Benutzer.query.get(request.form['benutzername'])
        if user:
            if user.passwort == request.form.get('passwort'):
                login_user(user, remember=True)
                return redirect(url_for(".profil", benutzername=user.benutzername, initialLogin=True))
            elif user.check_passwort(request.form['passwort']):
                login_user(user, remember=True)
                return redirect(url_for('site.home'))
            else:
                error_msg = 'Ungültige Anmeldedaten. Bitte überprüfe Benutzername und Passwort.'
        else:
            error_msg = 'Ungültige Anmeldedaten. Bitte überprüfe Benutzername und Passwort.'
    return render_template('login.html', error=error_msg)


@site.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('site.login'))


@site.route('/home')
@login_required
def home():
    ausleihen = Ausleihe.query.filter_by(
        ersteller_benutzername=current_user.benutzername).order_by(desc(Ausleihe.ts_von)).all()
    ausleihen_filtered_future = []
    ausleihen_filtered_past = []
    stats_list = []
    for a in ausleihen:
        materialien = []
        for m in a.materialien.split(","):
            materialien.append(Material.query.filter_by(idMaterial=m).first())
            stats_list.append(m)
        ausleihe = {'empfaenger': a.empfaenger, "ts_von": a.ts_von,
                    "ts_bis": a.ts_bis, "materialien": materialien}
        if a.ts_von > date.today():
            ausleihen_filtered_future.append(ausleihe)
        else:
            ausleihen_filtered_past.append(ausleihe)
    stats_dict = dict()
    stats_dict1 = dict()
    max_value = 0
    if len(stats_list) > 0:
        for i in stats_list:
            stats_dict[str(i)] = stats_dict.get(str(i), 0)+1
        materialien = Material.query.all()
        for m in materialien:
            stats_dict1[m.name] = stats_dict.get(
                str(m.idMaterial), 0) / len(stats_list)*100
        max_value = max(stats_dict1.values())
    return render_template('home.html', ausleihen_zukunft=ausleihen_filtered_future[:3], ausleihen_alt=ausleihen_filtered_past[:3], stats=stats_dict1, max=max_value)


@site.route("/benutzer", methods=['GET', 'POST'])
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

        return render_template('benutzer.html', benutzer_liste=liste, roles=rollen, edit=erlaubeBearbeiten)


@site.route('/profil/<benutzername>', methods=['GET', 'POST'])
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
                        return redirect(url_for("site.profil", benutzername=benutzername, missingPwdConfirm=True))
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
        return render_template('profil.html', user=user, roles=rollen, edit=edit_permission, hide_menu=hide_menu, error=error_msg)


@site.route("/kalender")
@login_required
def kalender():
    return render_template('kalender.html')


@site.route("/einstellungen")
@login_required
def einstellungen():
    return render_template('server_einstellungen.html')


@site.route('/scanner')
@login_required
def scanner():
    return render_template('scanner.html')


@site.route('/qrcode-generator', methods=['GET'])
@login_required
def qrcode_generator():
    materialien = Material.query.all()
    kategorien = Kategorie.query.all()
    return render_template('qrgenerator.html', materialListe=materialien, kategorienListe=kategorien)

@site.route("/auslagen")
@login_required
def auslagen_uebersicht():
    kategorienListe = AuslagenKategorie.query.all()
    return render_template("auslagen.html", kategorienListe=kategorienListe)
