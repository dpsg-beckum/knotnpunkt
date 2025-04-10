from datetime import date

from flask import Blueprint, Response, abort, current_app, request
from flask.helpers import url_for
from flask.templating import render_template
from flask_login import current_user
from flask_login.utils import login_required, login_user, logout_user
from sqlalchemy import desc
from werkzeug.utils import redirect

from ..database import db
from ..database.auslagen import AuslagenKategorie
from ..database.db import Benutzer
from ..database.exceptions import ElementAlreadyExists, ElementDoesNotExsist
from ..database.material import Ausleihe, Material
from .auslagen import auslagen_site
from .material import material_site
from .user import user_site

site = Blueprint("site", __name__, template_folder="templates")
site.register_blueprint(material_site)
site.register_blueprint(user_site)
site.register_blueprint(auslagen_site)


# insert current user for all templates
@site.context_processor
def inject_user():
    if not current_user.is_authenticated:
        return {}

    usr: Benutzer = current_user
    return dict(cuser=usr.to_dict(1))


@site.route('/')
def redirectToLogin():
    return redirect(url_for('site.login'))


@site.route("/login", methods=['GET', 'POST'])
def login():
    print(f"Login: {request.method}")
    error_msg = ""
    if current_user.is_authenticated:
        return redirect(url_for('site.home'))
    if request.args.get("newPassword"):
        error_msg = "Bitte melde dich mit deinem neuen Passwort an."
    if request.method == 'POST':
        try:
            user = Benutzer.get_via_id(request.form['benutzername'])
            if user.passwort == request.form.get('passwort'):
                login_user(user, remember=True)
                return redirect(url_for("site.user_site.profil", benutzername=user.benutzername, initialLogin=True))
            elif user.checkPassword(request.form['passwort']):
                login_user(user, remember=True)
                return redirect(url_for('site.home'))
            else:
                error_msg = 'Ungültige Anmeldedaten. Bitte überprüfe Benutzername und Passwort.'
        except ElementDoesNotExsist:
            error_msg = 'Ungültige Anmeldedaten. Bitte überprüfe Benutzername und Passwort.'
    return render_template('login.html', error=error_msg)


@site.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.login'))


@site.route('/home')
@login_required
def home():
    usr: Benutzer = current_user

    ausleihen = Ausleihe.filter_by(ersteller_benutzername=usr.benutzername)
    ausleihen = sorted(
        ausleihen, key=lambda x: x.ts_von, reverse=True)
    ausleihen_filtered_future = []
    ausleihen_filtered_past = []
    stats_list = []
    for a in ausleihen:
        materialien = []
        for m in a.materialien.split(","):
            materialien.append(Material.get_via_id(m))
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
        materialien = Material.get_all()
        for m in materialien:
            stats_dict1[m.name] = stats_dict.get(
                str(m.id), 0) / len(stats_list)*100
        max_value = max(stats_dict1.values())
    return render_template('home.html', ausleihen_zukunft=ausleihen_filtered_future[:3], ausleihen_alt=ausleihen_filtered_past[:3], stats=stats_dict1, max=max_value)


@site.route("/kalender")
@login_required
def kalender():
    return render_template('kalender.html')


@site.route("/einstellungen")
@login_required
def einstellungen():
    return render_template('server_einstellungen.html')


@site.get("/-demo")
def seed_demo_data():
    if not current_user.is_authenticated or not current_app.config.get("DEBUG"):
        abort(404)

    from ..database.demo_data import seed_demo_data

    try:
        seed_demo_data()
    except ElementAlreadyExists:
        return "Demo data already seeded", 409
    return "OK", 200
