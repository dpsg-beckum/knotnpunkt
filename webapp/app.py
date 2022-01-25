from email.policy import default
from os import name
from datetime import datetime as dt
from datetime import date
from statistics import median_grouped
from time import sleep          #time.sleep um die UI bei API-Anfragen zu testen
from flask import Flask, request, Response, jsonify     #jsonify macht direkt eine Flask.Response anstatt String
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
import humanize as hu

def util(datetime):
   _t = hu.i18n.activate("de_DE")
   return hu.naturaltime(dt.now()-dt.strptime(json.loads(datetime).get('zuletztGescannt'), '%Y-%m-%d %H:%M'))

def checkverfuegbarkeit(materialien):
    dict_verfuegbar = {}
    ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_beginn)).all()
    for m in materialien:
        if json.loads(m.Eigenschaften).get('zaehlbar',False):
            dict_verfuegbar[m.idMaterial] =json.loads(m.Eigenschaften).get('anzahl',1)
        else:
            dict_verfuegbar[m.idMaterial] = True
        for a in ausleihen:
            if int(m.idMaterial) in [int(x) for x in a.materialien.split(",")]:
                if a.ts_beginn <= date.today() <= a.ts_ende:
                    if json.loads(m.Eigenschaften).get('zaehlbar',False) == False:
                        dict_verfuegbar[m.idMaterial] = False
                    else:
                        dict_verfuegbar[m.idMaterial] = dict_verfuegbar[m.idMaterial] -1
    return dict_verfuegbar


logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s: %(message)s')
print(hu.naturaltime(dt.now()-dt.strptime("2021-11-01 10:23", '%Y-%m-%d %H:%M')))
app = Flask(__name__)
app.secret_key = b'c\xb4A+K\xf7\xe9\xab\xb4,\x0c\xc8\xec\x82\xf0\xde'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.globals.update(naturaltime=util)
db = SQLAlchemy(app, )
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def redirectToLogin():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('home'))
    error = None
    if request.method == 'POST': 
        user = Benutzer.query.get(request.form['benutzername'])
        if user:
            if user.passwort == request.form['passwort']:
                debug(f'{user.benutzername} hat sich angemeldet, Rolle: {user.Rolle.name}')
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else: 
                debug(f"Falsches Passwort für {request.form['benutzername']}")
                error = 'Benutzername oder Passwort falsch.'
        else:
            debug(f"Benutzername {request.form['benutzername']} ist nicht in der Datenbank vorhanden")
            error = 'Benutzername oder Passwort falsch.'
    return render_template('login.html', error = error)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html', apps=current_user.views())


@app.route("/benutzer", methods=['GET', 'POST'])
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




@app.route('/profil/<benutzername>', methods=['GET', 'POST'])
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

@app.route("/material", methods=['GET', 'POST'])
@login_required
def material():
    if request.method == 'POST':
        debug(request.form.get('rhArtNummer'))
        eigenschaften = {"anzahl": request.form.get('anzahl')}
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
        return render_template('material.html', apps=current_user.views(), materialListe=materialien, kategorienListe=kategorien, verfuegbarkeit = verfuegbarkeit,  jsonRef=json, huRef=hu, dtRef=dt)


@app.route('/material/<idMaterial>')
@login_required
def materialDetails(idMaterial):
    material_details = Material.query.filter_by(idMaterial = idMaterial).all()
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
    return render_template('material_details.html', apps=current_user.views(), material_details=material_details, ausleihListeZukunft = ausleihen_filtered_future, ausleihListeAlt = ausleihen_filtered_past, verfuegbarkeit = verfuegbarkeit, zuletzt_ausgeliehen_Tage = zuletzt_ausgeliehen_Tage, jsonRef=json, huRef=hu, dtRef=dt)

@app.route("/kalender")
@login_required
def kalender():
    return render_template('kalender.html', apps=current_user.views())

@app.route("/einstellungen")
@login_required
def einstellungen():
    return render_template('server_einstellungen.html', apps=current_user.views())

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@login_manager.user_loader
def user_loader(user_id):
    return Benutzer.query.get(user_id)


@app.route('/api/material')
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

@app.route('/api/material/checkout', methods=['POST'])
@login_required
def checkout():
    debug(request.form['id'])
    neue_aktivitaet = Aktivitaet(int(request.form.get('id')), dt.utcfromtimestamp(int(request.form.get('timestamp')[:-3])), int(request.form.get('menge')), current_user.benutzername, request.form.get('bemerkung'))
    db.session.add(neue_aktivitaet)
    db.session.commit()
    return Response(status=200)

# Datenbank-Klassen

class Aktivitaet(db.Model):
    __tablename__ = 'Aktivitaet'
    idAktivitaet = db.Column(db.Integer, primary_key=True)
    MaterialId = db.Column(db.ForeignKey('Material.idMaterial'), nullable=False)
    ausgecheckt = db.Column('ausgecheckt', db.DateTime, nullable=False)
    eingecheckt = db.Column('eingecheckt', db.DateTime, nullable=True)
    menge = db.Column('menge', db.Integer, nullable=False, default=1)
    ersteller_benutzername = db.Column('ersteller_benutzername',db.String(45),db.ForeignKey('Benutzer.benutzername'), nullable=False)
    bemerkung = db.Column('bemerkung',db.String(), nullable=True)
    Material = relationship('Material')
    Ersteller = relationship('Benutzer')

    def __init__(self, mat_id, ts_ausgecheckt, menge, benutzer, bemerkung) -> None:
        super().__init__()
        self.MaterialId = mat_id
        self.ausgecheckt = ts_ausgecheckt
        self.menge = menge
        self.ersteller_benutzername = benutzer
        self.bemerkung = bemerkung


class Ausleihe(db.Model):
    __tablename__ = 'Ausleihe'

    idAusleihe = db.Column(db.Integer, primary_key=True)
    ersteller_benutzername = db.Column('Benutzer_benutzername',db.String(45),db.ForeignKey('Benutzer.benutzername'), nullable=False, index=True)
    empfaenger = db.Column('empfaenger', db.String(45), nullable=True)
    ts_erstellt = db.Column('ts_erstellt', db.DateTime, nullable=False)
    ts_beginn = db.Column('ts_von', db.Date, nullable=False)
    ts_ende = db.Column('ts_bis', db.Date, nullable=False)
    beschreibung = db.Column('beschreibung',db.String(), nullable=False)
    materialien = db.Column('materialien',db.String(), nullable=False)
    Ersteller = relationship('Benutzer')

class Adresse(db.Model):
    __tablename__ = 'Adresse'

    idAdresse = db.Column(db.Integer, primary_key=True)
    straße = db.Column(db.String(45), nullable=False)
    hausnummer = db.Column(db.String(45))
    postleitzahl = db.Column(db.String(45))
    ort = db.Column(db.String(45), nullable=False)

    def __str__(self):
        return f"<Adresse {id}>"

class Kategorie(db.Model):
    __tablename__ = 'Kategorie'

    idKategorie = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    istZaehlbar = db.Column(db.String(45), nullable=False)

class Label(db.Model):
    __tablename__ = 'Label'

    idLabel = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    datentyp = db.Column(db.String(45), nullable=False)

class Benutzer(db.Model):
    __tablename__ = 'Benutzer'

    benutzername = db.Column(db.String(45), primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    emailAdresse = db.Column(db.String(45), nullable=False, unique=True)
    passwort = db.Column(db.String(45), nullable=False)
    adresseRef = db.Column(db.ForeignKey('Adresse.idAdresse'), nullable=False, index=True)
    rolleRef = db.Column('RolleRef',db.ForeignKey('Rolle.idRolle'), nullable=False, index=True)
    eingeloggt = db.Column(db.Boolean, nullable=False, default=False)
    Adresse = relationship('Adresse')
    Rolle= relationship('Rolle')

    def __init__(self, benutzername, name, emailAdresse, passwort, idRolle) -> None:
        super().__init__()
        self.benutzername = benutzername
        self.name = name
        self.emailAdresse = emailAdresse
        self.passwort = passwort
        self.adresseRef = 1
        self.rolleRef = idRolle
        self.eingeloggt = False

    def is_active(self):
        return True

    def is_authenticated(self):
        return self.eingeloggt

    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.benutzername

    def views(self):
        rechte = [key for key, value in self.rechte().items() if value == True]
        ansichten = []
        for r in rechte:
            if "kalender" in r:
                ansichten.append(('Kalender'))
            if "benutzer" in r:
                ansichten.append('Benutzer')
            if "material" in r:
                ansichten.append("Material")
            if "einstellungen" in r:
                ansichten.append("Einstellungen")
        return list(dict.fromkeys(ansichten))

    def rechte(self):
        return {
        'benutzerSchreiben': self.Rolle.schreibenBenutzer,
        'benutzerLesen': self.Rolle.lesenBenutzer,
        'materialSchreiben': self.Rolle.schreibenMaterial,
        'materialLesen': self.Rolle.lesenMaterial,
        'kalenderSchreiben': self.Rolle.schreibenKalender,
        'kalenderLesen': self.Rolle.lesenKalender,
        'einstellungenSchreiben': self.Rolle.schreibenEinstellungen,
        'einstellungenLesen': self.Rolle.lesenEinstellungen}
        

    def __repr__(self):
        return f"<User {self.benutzername} {self.Rolle.schreibenEinstellungen}>"

class Standarteigenschaft(db.Model):
    __tablename__ = 'Standarteigenschaft'

    Kategorie_idKategorie = db.Column(db.ForeignKey('Kategorie.idKategorie'), primary_key=True, nullable=False, index=True)
    Label_idLabel = db.Column(db.ForeignKey('Label.idLabel'), primary_key=True, nullable=False, index=True)
    wertInt = db.Column(db.String(45))
    wertString = db.Column(db.String(45))
    wertBool = db.Column(db.String(45))

    Kategorie = relationship('Kategorie')
    Label = relationship('Label')

class Aktion(db.Model):
    __tablename__ = 'Aktion'

    idAktion = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    beginn = db.Column(DATETIME(fsp=4), nullable=False)
    ende = db.Column(DATETIME(fsp=4), nullable=False)
    ansprechpartnerRef = db.Column(db.ForeignKey('Benutzer.benutzername'), nullable=False, index=True)
    Adresse_idAdresse = db.Column(db.ForeignKey('Adresse.idAdresse'), nullable=False, index=True)

    Adresse = relationship('Adresse')
    Benutzer = relationship('Benutzer')

class Lager(db.Model):
    __tablename__ = 'Lager'

    idLager = db.Column(db.Integer, primary_key=True)
    adresseRef = db.Column(db.ForeignKey('Adresse.idAdresse'), nullable=False, index=True)
    ansprechpartnerRef = db.Column(db.ForeignKey('Benutzer.benutzername'), nullable=False, index=True)

    Adresse = relationship('Adresse')
    Benutzer = relationship('Benutzer')

class Material(db.Model):
    __tablename__ = 'Material'
    idMaterial = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    Eigenschaften = db.Column(db.Text, nullable=True)
    Kategorie_idKategorie = db.Column(db.ForeignKey('Kategorie.idKategorie'), nullable=False, index=True)
    Kategorie = relationship('Kategorie')

    def __init__(self, name, kategorie, eigenschaften) -> None:
        super().__init__()
        self.name = name if name != '' else 'Unbennantes Material'
        self.Kategorie_idKategorie = kategorie
        self.Eigenschaften = eigenschaften

class Rolle(db.Model):
    __tablename__ = 'Rolle'

    idRolle = db.Column("idRolle", db.Integer(), primary_key=True)
    name = db.Column('name', db.String(45), nullable=False, unique=True)
    schreibenKalender = db.Column('schreibenKalender', db.Boolean(), default=False)
    lesenKalender = db.Column('lesenKalender', db.Boolean(), default=False)
    schreibenBenutzer = db.Column('schreibenBenutzer', db.Boolean(), default=False)
    lesenBenutzer = db.Column('lesenBenutzer', db.Boolean(), default=False)
    schreibenMaterial = db.Column('schreibenMaterial', db.Boolean(), default=False)
    lesenMaterial = db.Column('lesenMaterial', db.Boolean(), default=False)
    schreibenEinstellungen = db.Column('schreibenEinstellungen', db.Boolean(), default=False)
    lesenEinstellungen = db.Column('lesenEinstellungen', db.Boolean(), default=False)

    def __str__(self):
        return f"<Rolle {self.name}>"
    
class Eigenschaft(db.Model):
    __tablename__ = 'Eigenschaft'

    Material_idMaterial = db.Column(db.ForeignKey('Material.idMaterial'), primary_key=True, nullable=False, index=True)
    Label_idLabel = db.Column(db.ForeignKey('Label.idLabel'), primary_key=True, nullable=False, index=True)
    wertInt = db.Column(db.String(45))
    wertString = db.Column(db.String(45))
    wertBool = db.Column(db.String(45))

    Label = relationship('Label')
    Material = relationship('Material')


if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", ssl_context='adhoc')