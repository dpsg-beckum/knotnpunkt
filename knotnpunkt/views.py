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
    Adresse
)
from .utils import checkverfuegbarkeit


views = Blueprint("views", __name__, template_folder="templates")


@views.route('/')
def redirectToLogin():
    return redirect(url_for('views.login'))


@views.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('views.home'))
    error = None
    if request.method == 'POST': 
        user = Benutzer.query.get(request.form['benutzername'])
        if user:
            if user.passwort == request.form['passwort']:
                debug(f'{user.benutzername} hat sich angemeldet, Rolle: {user.Rolle.name}')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else: 
                debug(f"Falsches Passwort für {request.form['benutzername']}")
                error = 'Benutzername oder Passwort falsch.'
        else:
            debug(f"Benutzername {request.form['benutzername']} ist nicht in der Datenbank vorhanden")
            error = 'Benutzername oder Passwort falsch.'
    return render_template('login.html', error = error)


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
    return render_template('home.html', apps=current_user.views())


@views.route("/benutzer", methods=['GET', 'POST'])
@login_required
def benutzer():
    if request.method =='POST':
        debug(request.form)
        debug(Rolle.query.filter_by(name="admin").first().idRolle)
        neuerBenutzer = Benutzer(request.form.get('benutzername'), request.form.get('name'), request.form.get('email'), f"{request.form.get('benutzername')}", Rolle.query.filter_by(name=request.form.get('rolle')).first().idRolle)
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
        
        return render_template('benutzer.html', apps=current_user.views(), benutzer_liste=liste, roles=rollen, edit=erlaubeBearbeiten)


@views.route('/profil/<benutzername>', methods=['GET', 'POST'])
@login_required
def profil(benutzername):
    fehlermeldung = ""
    if current_user.Rolle.lesenBenutzer or current_user.benutzername == benutzername:
        if request.method== 'POST':
            debug(request.form)
            user = Benutzer.query.get(benutzername)
            if request.form.get("delete", "off") == 'on':
                db.session.delete(user)
                db.session.commit()
                debug("user gelöscht")
                return redirect('/benutzer')
            else:
                user.benutzername =  request.form['benutzername']
                user.name = request.form['name']
                user.email = request.form['email']
                if request.form.get('rolle'):
                    user.rolleRef = Rolle.query.filter_by(name=request.form.get('rolle')).first().idRolle
                if request.form.get('passwort', None):
                    if request.form.get('passwort') == request.form.get('passwortBestaetigung'):
                        user.passwort = request.form.get('passwort')
                        debug("Passwort wurde geaendert!")
                        db.session.add(user)
                        db.session.commit()
                    else:
                        fehlermeldung = "Bitte bestätige dein neues Passwort"
                db.session.add(user)
                db.session.commit()        
                return redirect('/benutzer')
        else:
            user = Benutzer.query.get(benutzername)
            rollen = Rolle.query.all()
            if current_user.Rolle.schreibenBenutzer and user.Rolle.name != 'admin' or current_user.Rolle.name == 'admin':
                erlaubeBearbeiten = True
            else:
                erlaubeBearbeiten = False
            return render_template('profil.html', apps=current_user.views(), user=user, roles = rollen, edit=erlaubeBearbeiten, error=fehlermeldung)
    else:
        return Response(f'Du hast leider keinen Zugriff auf das Profil von {benutzername}.', 401)


@views.route("/material", methods=['GET', 'POST'])
@login_required
def material():
    if request.method == 'POST':
        debug(request.form.get('rhArtNummer'))
        eigenschaften = {"anzahl": int(request.form.get('anzahl'))}
        if request.form.get('farbeCheckbox'):
            eigenschaften['farbe'] = request.form.get('farbe')
        if request.form.get('rhArtNummer'):
            eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
        debug(eigenschaften)
        if int(eigenschaften['anzahl']) >1:
            eigenschaften['verfuegbar'] = 1
        eigenschaften['zuletztGescannt'] = dt.strftime(dt.now(), "%Y-%m-%d %H:%M")
        neuesMaterial = Material(request.form.get('name'), request.form.get('kategorie'), json.dumps(eigenschaften))
        db.session.add(neuesMaterial)
        db.session.commit()
        return redirect('/material')
    else:
        materialien = Material.query.all()
        verfuegbarkeit = checkverfuegbarkeit(materialien)
        kategorien = Kategorie.query.all()
        debug(current_user.benutzername)
        return render_template('material.html', apps=current_user.views(), materialListe=materialien, kategorienListe=kategorien, verfuegbarkeit = verfuegbarkeit,  jsonRef=json, huRef=hu, dtRef=dt)


@views.route('/material/<idMaterial>', methods=['GET', 'POST'])
@login_required
def materialDetails(idMaterial):
    if request.method == 'POST':
        material_update = Material.query.filter_by(idMaterial = idMaterial).first()
        material_update.name = request.form.get('name')
        material_update.Kategorie_idKategorie = request.form.get('kategorie')
        eigenschaften = json.loads(material_update.Eigenschaften)
        if request.form.get('farbeCheckbox'):
            eigenschaften['farbe'] = request.form.get('farbe')
        if request.form.get('rhArtNummer'):
            eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
        if request.form.get('anzahl'):
            if int(request.form.get('anzahl'))>1:
                eigenschaften['anzahl'] = int(request.form.get('anzahl'))
                eigenschaften['zaehlbar'] = True
            else:
                eigenschaften['zaehlbar'] = False
        material_update.Eigenschaften = json.dumps(eigenschaften)
        db.session.commit()
        return redirect('/material/'+idMaterial)
    else:
        material_details = Material.query.filter_by(idMaterial = idMaterial).all()
        materialien = Material.query.all()
        ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_beginn)).all() #Hier schon direkt Filtern ob MaterialID(Int) in Ausgeliehenem Material(Str) ist? 
        ausleihen_filtered_future = []
        ausleihen_filtered_past = []
        verfuegbarkeit = checkverfuegbarkeit(material_details)
        for a in ausleihen:
            if int(idMaterial) in [int(x) for x in a.materialien.split(",")]:
                if a.ts_beginn > date.today():
                    ausleihen_filtered_future.append(a)
                else:
                    ausleihen_filtered_past.append(a)
        if len(ausleihen_filtered_past):
            zuletzt_ausgeliehen_Tage = (date.today() - ausleihen_filtered_past[0].ts_beginn).days
        else: 
            zuletzt_ausgeliehen_Tage = None
        kategorien = Kategorie.query.all()
        return render_template('material_details.html', apps=current_user.views(), material_details=material_details, materialListe = materialien, kategorienListe=kategorien, ausleihListeZukunft = ausleihen_filtered_future, ausleihListeAlt = ausleihen_filtered_past, verfuegbarkeit = verfuegbarkeit, zuletzt_ausgeliehen_Tage = zuletzt_ausgeliehen_Tage, jsonRef=json, huRef=hu, dtRef=dt)


@views.route('/reservieren/<idMaterial>', methods=['POST'])
@login_required
def materialReservieren(idMaterial):
    debug(request.form.get('reservierte_Materialien'))
    neueReservierung = Ausleihe(
        ersteller_benutzername = current_user.benutzername,
        ts_erstellt = dt.now(),
        ts_beginn = dt.strptime(request.form.get('reservieren_von'), "%Y-%m-%d"), 
        ts_ende = dt.strptime(request.form.get('reservieren_bis'), "%Y-%m-%d"),
        materialien = request.form.get('reservierte_Materialien'),
        empfaenger = request.form.get('empfaenger') if request.form.get('empfaenger') else current_user.benutzername,
        beschreibung= request.form.get('beschreibung'))
    db.session.add(neueReservierung)
    db.session.commit()
    return redirect('/material')


@views.route("/kalender")
@login_required
def kalender():
    return render_template('kalender.html', apps=current_user.views())


@views.route("/einstellungen")
@login_required
def einstellungen():
    return render_template('server_einstellungen.html', apps=current_user.views())


@views.route('/scanner')
@login_required
def scanner():
    return render_template('scanner.html')

@views.route('/qrcode-generator', methods=['GET'])
@login_required
def qrcode_generator():
    materialien = Material.query.all()
    kategorien = Kategorie.query.all()
    return render_template('qrgenerator.html', apps=current_user.views(), materialListe = materialien, kategorienListe=kategorien)



@views.route('/api/material')
@login_required
def material_api():
    #sleep(1)  # Verzögerung um UI zu testen. VORSICHT: sleep verzögert Sekunden, nicht Millisekunden
    material = Material.query.filter_by(idMaterial = request.args.get('id')).first()
    verfuegbarkeit = checkverfuegbarkeit([material])
    if verfuegbarkeit.get(material.idMaterial):     # Hier die Abfrage nach dem Ende der Reservierung...
        ...
    else:                                           # ...oder nach dem Beginn der Nächsten
        ...
    antwort = {'verfuegbarkeit': verfuegbarkeit,'id': material.idMaterial, 'name': material.name, 'kategorie': {'id': material.Kategorie.idKategorie, 'name':material.Kategorie.name}, 'eigenschaften': json.loads(material.Eigenschaften)}
    return jsonify(antwort)


@views.route('/api/material/checkout', methods=['POST'])
@login_required
def checkout():
    debug(request.form['id'])
    neue_aktivitaet = Aktivitaet(int(request.form.get('id')), dt.utcfromtimestamp(int(request.form.get('timestamp')[:-3])), int(request.form.get('menge')), current_user.benutzername, request.form.get('bemerkung'))
    db.session.add(neue_aktivitaet)
    db.session.commit()
    return Response(status=200)


# if __name__ == '__main__':
#     app.run(debug = True, host="0.0.0.0", ssl_context='adhoc')