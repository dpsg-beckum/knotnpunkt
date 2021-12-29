from flask import Flask, request
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import LoginManager, current_user
from flask_login.utils import login_required, login_user, logout_user
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.dialects.mysql import DATETIME
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import debug

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s: %(message)s')

app = Flask(__name__)
app.secret_key = b'c\xb4A+K\xf7\xe9\xab\xb4,\x0c\xc8\xec\x82\xf0\xde'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.db'
db = SQLAlchemy(app)
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
    user = current_user
    views = user.views()
    return render_template('home.html', apps=views)

@app.route("/benutzer")
@login_required
def benutzer():
    return "Benutzerseiten"

@app.route("/material")
@login_required
def material():
    return "Material"

@app.route("/kalender")
@login_required
def kalender():
    return "Kalender"

@app.route("/einstellungen")
@login_required
def einstellungen():
    return "Einstellungen"

@login_manager.user_loader
def user_loader(user_id):
    return Benutzer.query.get(user_id)



# Datenbank-Klassen
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
    Kategorie_idKategorie = db.Column(db.ForeignKey('Kategorie.idKategorie'), nullable=False, index=True)
    Lager_idLager = db.Column(db.ForeignKey('Lager.idLager'), nullable=False, index=True)

    Kategorie = relationship('Kategorie')
    Lager = relationship('Lager')

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
    app.run(debug = True, host="0.0.0.0")