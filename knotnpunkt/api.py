from email.policy import default
from os import name
from datetime import datetime as dt
from datetime import date
from statistics import median_grouped
from time import sleep
from urllib import response          #time.sleep um die UI bei API-Anfragen zu testen
from flask import Flask, request, Response, jsonify, Blueprint , abort    #jsonify macht direkt eine Flask.Response anstatt String
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import LoginManager, current_user
from flask_login.utils import login_required, login_user, logout_user
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean, Integer
from sqlalchemy import desc
from sqlalchemy.dialects.mysql import DATETIME
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import debug
import json
from .models import * 
from time import sleep
# from . import login_manager
# from . import app, login_manager


api = Blueprint("api", __name__, template_folder="templates", url_prefix="/api")

def util(datetime):
    ...
#    _t = hu.i18n.activate("de_DE")
#    return hu.naturaltime(dt.now()-dt.strptime(json.loads(datetime).get('zuletztGescannt'), '%Y-%m-%d %H:%M'))

# def checkverfuegbarkeit(materialien):
#     dict_verfuegbar = {}
#     ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_beginn)).all()
#     for m in materialien:
#         if json.loads(m.Eigenschaften).get('zaehlbar',False):
#             dict_verfuegbar[m.idMaterial] =json.loads(m.Eigenschaften).get('anzahl',1)
#         else:
#             dict_verfuegbar[m.idMaterial] = True
#         for a in ausleihen:
#             if int(m.idMaterial) in [int(x) for x in a.materialien.split(",")]:
#                 if a.ts_beginn <= date.today() <= a.ts_ende:
#                     if json.loads(m.Eigenschaften).get('zaehlbar',False) == False:
#                         dict_verfuegbar[m.idMaterial] = False
#                     else:
#                         dict_verfuegbar[m.idMaterial] = dict_verfuegbar[m.idMaterial] -1
#     return dict_verfuegbar


# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s: %(message)s')
# app = Flask(__name__)
# app.secret_key = b'c\xb4A+K\xf7\xe9\xab\xb4,\x0c\xc8\xec\x82\xf0\xde'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.jinja_env.globals.update(naturaltime=util)
# login_manager = LoginManager()
# login_manager.init_app(app)
# db = SQLAlchemy(app)
# db.init_app(app)
# migrate = Migrate(app, db)


# @api.route('/')
# def redirectToLogin():
#     return redirect(url_for('login'))

@api.route('/debug')
def debugrequest():
    # raise TypeError()
    response = Benutzer.query.all()
    print(response)
    return jsonify(response)


@api.route('/accountInfo')
def accountInfo():
    response ={"action": "/api/accountInfo", "user": {"authenticated": False}}
    if current_user.is_authenticated:
        response["user"]["authenticated"] = True
        response["user"]["benutzername"]=current_user.benutzername
        response["user"]["apps"] = current_user.views()
        response["user"]["emailAdresse"] = current_user.emailAdresse
        response["user"]["name"] = current_user.name
        response["user"]["rolle"] = current_user.Rolle.name
    return jsonify(response)


@api.route("/login", methods=['POST'])
def login():
    data = json.loads(request.data)
    response = {"action": "/api/login"}
    print(data['benutzername'])
    user = Benutzer.query.get(data['benutzername'])
    # Prüfe ob Benutzername vergeben ist und das richtige Passwort angegeben wurde
    if not user or not user.passwort == data['passwort']: 
        debug(f"Falsche Anmeldeinformationen")
        response["success"] = False
        response["error"] = 'Benutzername oder Passwort falsch.'
        return jsonify(response)
    response["benutzername"] = user.benutzername
    # response["rolle"] = user.Rolle.name
    login_user(user, remember=False)
    debug(f'{user.benutzername} hat sich angemeldet, Rolle: {user.Rolle.name}')
    # response["apps"] = user.views()
    response["success"] = True           
    return jsonify(response)

@api.route('/logout', methods=['POST'])
@login_required
def logout():
    response =  {"action": "/api/logout", "benutzername": current_user.benutzername}
    if logout_user():
        response["success"] = True
    return jsonify(response)


# @api.route('/home')
# @login_required
# def home():
#     return render_template('home.html', apps=current_user.views())


@api.route("/benutzer/<benutzername>", methods=['GET'])
@login_required
def benutzerprofil(benutzername):
    sleep(0.4)
    user = user = Benutzer.query.get(benutzername)
    response = {"action": f"/api/benutzer{benutzername}"}
    if user:
        response["success"] = True
        response["user"]= {
        "authenticated": True,
        "benutzername":current_user.benutzername,
        "apps": current_user.views(),
        "emailAdresse": current_user.emailAdresse,
        "name": current_user.name,
        "rolle": current_user.Rolle.name,
        }
    return response


# Old POST handling of benutzer API
    # if request.method =='POST':
    #     debug(request.form)
    #     debug(Rolle.query.filter_by(name="admin").first().idRolle)
    #     neuerBenutzer = Benutzer(request.form.get('benutzername'), request.form.get('name'), request.form.get('email'), f"{request.form.get('benutzername')}", Rolle.query.filter_by(name=request.form.get('rolle')).first().idRolle)
    #     db.session.add(neuerBenutzer)
    #     db.session.commit()
    #     return redirect("/benutzer")
    # else:

# @api.route('/profil/<benutzername>', methods=['GET', 'POST'])
# @login_required
# def profil(benutzername):
#     fehlermeldung = ""
#     if current_user.Rolle.lesenBenutzer or current_user.benutzername == benutzername:
#         if request.method== 'POST':
#             debug(request.form)
#             user = Benutzer.query.get(benutzername)
#             if request.form.get("delete", "off") == 'on':
#                 db.session.delete(user)
#                 db.session.commit()
#                 debug("user gelöscht")
#                 return redirect('/benutzer')
#             else:
#                 user.benutzername =  request.form['benutzername']
#                 user.name = request.form['name']
#                 user.email = request.form['email']
#                 if request.form.get('rolle'):
#                     user.rolleRef = Rolle.query.filter_by(name=request.form.get('rolle')).first().idRolle
#                 if request.form.get('passwort', None):
#                     if request.form.get('passwort') == request.form.get('passwortBestaetigung'):
#                         user.passwort = request.form.get('passwort')
#                         debug("Passwort wurde geaendert!")
#                         db.session.add(user)
#                         db.session.commit()
#                     else:
#                         fehlermeldung = "Bitte bestätige dein neues Passwort"
#                 db.session.add(user)
#                 db.session.commit()        
#                 return redirect('/benutzer')
#         else:
#             user = Benutzer.query.get(benutzername)
#             rollen = Rolle.query.all()
#             if current_user.Rolle.schreibenBenutzer and user.Rolle.name != 'admin' or current_user.Rolle.name == 'admin':
#                 erlaubeBearbeiten = True
#             else:
#                 erlaubeBearbeiten = False
#             return render_template('profil.html', apps=current_user.views(), user=user, roles = rollen, edit=erlaubeBearbeiten, error=fehlermeldung)
#     else:
#         return Response(f'Du hast leider keinen Zugriff auf das Profil von {benutzername}.', 401)

# @api.route("/material", methods=['GET', 'POST'])
# @login_required
# def material():
#     if request.method == 'POST':
#         debug(request.form.get('rhArtNummer'))
#         eigenschaften = {"anzahl": int(request.form.get('anzahl'))}
#         if request.form.get('farbeCheckbox'):
#             eigenschaften['farbe'] = request.form.get('farbe')
#         if request.form.get('rhArtNummer'):
#             eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
#         debug(eigenschaften)
#         if int(eigenschaften['anzahl']) >1:
#             eigenschaften['verfuegbar'] = 1
#         eigenschaften['zuletztGescannt'] = dt.strftime(dt.now(), "%Y-%m-%d %H:%M")
#         neuesMaterial = Material(request.form.get('name'), request.form.get('kategorie'), json.dumps(eigenschaften))
#         db.session.add(neuesMaterial)
#         db.session.commit()
#         return redirect('/material')
#     else:
#         materialien = Material.query.all()
#         verfuegbarkeit = checkverfuegbarkeit(materialien)
#         kategorien = Kategorie.query.all()
#         debug(current_user.benutzername)
#         return render_template('material.html', apps=current_user.views(), materialListe=materialien, kategorienListe=kategorien, verfuegbarkeit = verfuegbarkeit,  jsonRef=json, dtRef=dt)


# @api.route('/material/<idMaterial>', methods=['GET', 'POST'])
# @login_required
# def materialDetails(idMaterial):
#     if request.method == 'POST':
#         material_update = Material.query.filter_by(idMaterial = idMaterial).first()
#         material_update.name = request.form.get('name')
#         material_update.Kategorie_idKategorie = request.form.get('kategorie')
#         eigenschaften = json.loads(material_update.Eigenschaften)
#         debug(type(eigenschaften))
#         if request.form.get('farbeCheckbox'):
#             eigenschaften['farbe'] = request.form.get('farbe')
#         if request.form.get('rhArtNummer'):
#             eigenschaften['rhArtNummer'] = request.form.get('rhArtNummer')
#         if request.form.get('anzahl'):
#             if int(request.form.get('anzahl'))>1:
#                 eigenschaften['anzahl'] = int(request.form.get('anzahl'))
#                 eigenschaften['zaehlbar'] = True
#             else:
#                 eigenschaften['zaehlbar'] = False
#         material_update.Eigenschaften = json.dumps(eigenschaften)
#         db.session.commit()
#         return redirect('/material/'+idMaterial)
#     else:
#         material_details = Material.query.filter_by(idMaterial = idMaterial).all()
#         materialien = Material.query.all()
#         ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_beginn)).all() #Hier schon direkt Filtern ob MaterialID(Int) in Ausgeliehenem Material(Str) ist? 
#         ausleihen_filtered_future = []
#         ausleihen_filtered_past = []
#         verfuegbarkeit = checkverfuegbarkeit(material_details)
#         for a in ausleihen:
#             if int(idMaterial) in [int(x) for x in a.materialien.split(",")]:
#                 if a.ts_beginn > date.today():
#                     ausleihen_filtered_future.append(a)
#                 else:
#                     ausleihen_filtered_past.append(a)
#         if len(ausleihen_filtered_past):
#             zuletzt_ausgeliehen_Tage = (date.today() - ausleihen_filtered_past[0].ts_beginn).days
#         else: 
#             zuletzt_ausgeliehen_Tage = None
#         kategorien = Kategorie.query.all()
#         return render_template('material_details.html', apps=current_user.views(), material_details=material_details, materialListe = materialien, kategorienListe=kategorien, ausleihListeZukunft = ausleihen_filtered_future, ausleihListeAlt = ausleihen_filtered_past, verfuegbarkeit = verfuegbarkeit, zuletzt_ausgeliehen_Tage = zuletzt_ausgeliehen_Tage, jsonRef=json, dtRef=dt)

# @api.route('/reservieren/<idMaterial>', methods=['POST'])
# @login_required
# def materialReservieren(idMaterial):
#     neueReservierung = Ausleihe(ersteller_benutzername = current_user.benutzername,ts_erstellt = dt.now(),ts_beginn = dt.strptime(request.form.get('reservieren_von'), "%Y-%m-%d"), ts_ende = dt.strptime(request.form.get('reservieren_bis'), "%Y-%m-%d"),materialien = str(idMaterial),empfaenger = request.form.get('empfaenger'), beschreibung= request.form.get('beschreibung'))
#     db.session.add(neueReservierung)
#     db.session.commit()
#     return redirect('/material')

# @api.route("/kalender")
# @login_required
# def kalender():
#     return render_template('kalender.html', apps=current_user.views())

# @api.route("/einstellungen")
# @login_required
# def einstellungen():
#     return render_template('server_einstellungen.html', apps=current_user.views())

# @api.route('/scanner')
# def scanner():
#     return render_template('scanner.html')

# @login_manager.user_loader
# def user_loader(user_id):
#     return Benutzer.query.get(user_id)

#### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API #####
# @api.route('/api/material')
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

# @api.route('/api/material/checkout', methods=['POST'])
# @login_required
# def checkout():
#     debug(request.form['id'])
#     neue_aktivitaet = Aktivitaet(int(request.form.get('id')), dt.utcfromtimestamp(int(request.form.get('timestamp')[:-3])), int(request.form.get('menge')), current_user.benutzername, request.form.get('bemerkung'))
#     db.session.add(neue_aktivitaet)
#     db.session.commit()
#     return Response(status=200)



#### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API ##### API #####
