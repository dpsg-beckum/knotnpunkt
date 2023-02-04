from datetime import datetime as dt
from datetime import date
from flask import request, Response, jsonify, Blueprint
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from sqlalchemy import desc
from werkzeug.utils import redirect
from logging import debug
# from .. import logger
import json
import base64
import humanize as hu
from .database import db
from .database.db import (
    Benutzer,
    Material,
    Aktion,
    Aktivitaet,
    Kategorie,
    Ausleihe,
    Rolle,
    Adresse,
    Img
)
from .utils import checkverfuegbarkeit

views = Blueprint("views", __name__, template_folder="templates")


@views.route('/')
def redirectToLogin():
    return redirect(url_for('views.login'))


@views.route("/login", methods=['GET', 'POST'])
def login():
    error_msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
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
                return redirect(url_for('views.home'))
            else:
                error_msg = 'Ungültige Anmeldedaten. Bitte überprüfe Benutzername und Passwort.'
        else:
            error_msg = 'Ungültige Anmeldedaten. Bitte überprüfe Benutzername und Passwort.'
    return render_template('login.html', error=error_msg)


@views.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('views.login'))


@views.route('/home')
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


@views.route("/benutzer", methods=['GET', 'POST'])
@login_required
def benutzer():
    if request.method == 'POST':
        neuerBenutzer = Benutzer(request.form.get('benutzername'), request.form.get('name'), request.form.get(
            'email'), f"{request.form.get('benutzername')}", Rolle.query.filter_by(name=request.form.get('rolle')).first().idRolle)
        db.session.add(neuerBenutzer)
        db.session.commit()
        return redirect("/benutzer")
    else:
        if current_user.Rolle.schreibenBenutzer:
            erlaubeBearbeiten = True
        else:
            erlaubeBearbeiten = False
        liste = Benutzer.query.order_by(Benutzer.name).all()
        rollen = Rolle.query.all()

        return render_template('benutzer.html', benutzer_liste=liste, roles=rollen, edit=erlaubeBearbeiten)


@views.route('/profil/<benutzername>', methods=['GET', 'POST'])
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
                return redirect('/benutzer')
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
                        return redirect(url_for("views.login", newPassword=True))
                    else:
                        error_msg = "Änderung fehlgeschlagen. Bitte bestätige dein Passwort."
                        return redirect(url_for("views.profil", benutzername=benutzername, missingPwdConfirm=True))
                db.session.add(user)
                db.session.commit()
                return redirect('/benutzer')
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


@views.route("/material", methods=['GET', 'POST'])
@login_required
def material():
    if request.method == 'POST':
        eigenschaften = {"anzahl": int(request.form.get('anzahl'))}
        if request.form.get('beschreibung'):
            eigenschaften['beschreibung'] = request.form.get('beschreibung')
        if request.form.get('rhArtNummer'):
            eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
        if request.form.get('verpackung'):
            eigenschaften['verpackung'] = request.form.get('verpackung')
        if int(eigenschaften['anzahl']) > 1:
            eigenschaften['verfuegbar'] = 1
        eigenschaften['zuletztGescannt'] = dt.strftime(
            dt.now(), "%Y-%m-%d %H:%M")
        neuesMaterial = Material(request.form.get(
            'name'), request.form.get('kategorie'), eigenschaften)
        db.session.add(neuesMaterial)
        db.session.commit()
        return redirect('/material')
    else:
        materialien = Material.query.all()
        verfuegbarkeit = checkverfuegbarkeit(materialien)
        kategorien = Kategorie.query.all()
        material_list = []
        for material in materialien:
            id = material.idMaterial
            image = Img.query.filter_by(Material_idMaterial=id).first()
            if image != None:
                material_list.append(
                    [material, base64.b64encode(image.img).decode('utf-8')])
            else:
                material_list.append([material, None])
        return render_template('material.html', materialListe=material_list, kategorienListe=kategorien, verfuegbarkeit=verfuegbarkeit,  jsonRef=json, huRef=hu, dtRef=dt)


@views.route('/material/<idMaterial>', methods=['GET'])
@login_required
def materialDetails(idMaterial):
    material_details = Material.query.filter_by(idMaterial=idMaterial).all()
    materialien = Material.query.all()
    # Hier schon direkt Filtern ob MaterialID(Int) in Ausgeliehenem Material(Str) ist?
    ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_von)).all()
    ausleihen_filtered_future = []
    ausleihen_filtered_past = []
    verfuegbarkeit = checkverfuegbarkeit(material_details)
    for a in ausleihen:
        if int(idMaterial) in [int(x) for x in a.materialien.split(",")]:
            if a.ts_von > date.today():
                ausleihen_filtered_future.append(a)
            else:
                ausleihen_filtered_past.append(a)
    if len(ausleihen_filtered_past):
        zuletzt_ausgeliehen_Tage = (
            date.today() - ausleihen_filtered_past[0].ts_von).days
    else:
        zuletzt_ausgeliehen_Tage = None
    kategorien = Kategorie.query.all()
    material_images = Img.query.filter_by(Material_idMaterial=idMaterial).all()
    img_id_list = []
    if material_images:
        for image in material_images:
            img_id_list.append(
                [image.img_id, base64.b64encode(image.img).decode('utf-8')])
    else:
        img_id_list.append(None)
    return render_template('material_details.html', material_details=material_details, materialListe=materialien, kategorienListe=kategorien, ausleihListeZukunft=ausleihen_filtered_future, ausleihListeAlt=ausleihen_filtered_past, verfuegbarkeit=verfuegbarkeit, zuletzt_ausgeliehen_Tage=zuletzt_ausgeliehen_Tage, jsonRef=json, huRef=hu, dtRef=dt, images=img_id_list)


@views.route('/material/edit/<idMaterial>', methods=['POST'])
@login_required
def materialDetailsEdit(idMaterial):
    material_update = Material.query.filter_by(idMaterial=idMaterial).first()
    material_update.name = request.form.get('name')
    material_update.Kategorie_idKategorie = request.form.get('kategorie')
    eigenschaften = dict(material_update.Eigenschaften)
    debug(eigenschaften)
    debug(f"{request.form.get('beschreibung')},{request.form.get('rhArtNummer')},{request.form.get('verpackung')}")
    if request.form.get('beschreibung'):
        eigenschaften['beschreibung'] = request.form.get('beschreibung')
    if request.form.get('rhArtNummer'):
        eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
    if request.form.get('verpackung'):
        eigenschaften['verpackung'] = request.form.get('verpackung')
    if request.form.get('anzahl'):
        if int(request.form.get('anzahl')) > 1:
            eigenschaften['anzahl'] = int(request.form.get('anzahl'))
            eigenschaften['zaehlbar'] = True
        else:
            eigenschaften['zaehlbar'] = False
    material_update.Eigenschaften = eigenschaften
    debug(eigenschaften)
    debug(material_update.Eigenschaften)
    db.session.commit()
    return redirect('/material/'+idMaterial)


@views.route('/reservieren/<idMaterial>', methods=['POST'])
@login_required
def materialReservieren(idMaterial):
    debug(request.form.get('reservierte_Materialien'))
    neueReservierung = Ausleihe(
        ersteller_benutzername=current_user.benutzername,
        ts_erstellt=dt.now(),
        ts_von=dt.strptime(request.form.get('reservieren_von'), "%Y-%m-%d"),
        ts_bis=dt.strptime(request.form.get('reservieren_bis'), "%Y-%m-%d"),
        materialien=request.form.get('reservierte_Materialien'),
        empfaenger=request.form.get('empfaenger') if request.form.get(
            'empfaenger') else current_user.benutzername,
        beschreibung=request.form.get('beschreibung'))
    db.session.add(neueReservierung)
    db.session.commit()
    return redirect('/material')


@views.route('/img/upload/<idMaterial>', methods=['POST'])
@login_required
def upload_img(idMaterial):
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400
    material_id = idMaterial
    mimetype = pic.mimetype
    if not material_id or not mimetype:
        return 'Bad upload!', 400
    img = Img(img=pic.read(), Material_idMaterial=material_id, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()
    return redirect('/material/'+idMaterial)


@views.route('/img/delete/<id>/<idMaterial>')  # , methods=['POST']
@login_required
def delete_img(id, idMaterial):
    Img.query.filter_by(img_id=id).delete()
    db.session.commit()
    return redirect('/material/'+idMaterial)


@views.route("/kalender")
@login_required
def kalender():
    return render_template('kalender.html')


@views.route("/einstellungen")
@login_required
def einstellungen():
    return render_template('server_einstellungen.html')


@views.route('/scanner')
@login_required
def scanner():
    return render_template('scanner.html')


@views.route('/qrcode-generator', methods=['GET'])
@login_required
def qrcode_generator():
    materialien = Material.query.all()
    kategorien = Kategorie.query.all()
    return render_template('qrgenerator.html', materialListe=materialien, kategorienListe=kategorien)


# @views.route('/api/material')
# @login_required
# def material_api():
#     #sleep(1)  # Verzögerung um UI zu testen. VORSICHT: sleep verzögert Sekunden, nicht Millisekunden
#     material = Material.query.filter_by(idMaterial = request.args.get('id')).first()
#     verfuegbarkeit = checkverfuegbarkeit([material])
#     if verfuegbarkeit.get(material.idMaterial):     # Hier die Abfrage nach dem Ende der Reservierung...
#         ...
#     else:                                           # ...oder nach dem Beginn der Nächsten
#         ...
#     antwort = {'verfuegbarkeit': verfuegbarkeit,'id': material.idMaterial, 'name': material.name, 'kategorie': {'id': material.Kategorie.idKategorie, 'name':material.Kategorie.name}, 'eigenschaften': json.loads(material.Eigenschaften)}
#     return jsonify(antwort)


# @views.route('/api/material/checkout', methods=['POST'])
# @login_required
# def checkout():
#     debug(request.form['id'])
#     neue_aktivitaet = Aktivitaet(int(request.form.get('id')), dt.utcfromtimestamp(int(request.form.get('timestamp')[:-3])), int(request.form.get('menge')), current_user.benutzername, request.form.get('bemerkung'))
#     db.session.add(neue_aktivitaet)
#     db.session.commit()
#     return Response(status=200)


# if __name__ == '__main__':
#     app.run(debug = True, host="0.0.0.0", ssl_context='adhoc')
