import json
from datetime import date
from datetime import datetime as dt

import humanize as hu
from sqlalchemy import desc

from .database.material import Ausleihe, Material


def convertTime(datetime):
    _t = hu.i18n.activate("de_DE")
    return hu.naturaltime(dt.now()-dt.strptime(datetime.get('zuletztGescannt'), '%Y-%m-%d %H:%M'))


def checkverfuegbarkeit(materialien: list[Material]) -> dict:
    dict_verfuegbar = {}
    ausleihen = Ausleihe.get_all()
    # Sort ausleihen by ts_von
    ausleihen = sorted(
        ausleihen, key=lambda x: x.ts_von, reverse=True)

    # ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_von)).all()
    for m in materialien:
        if m.Eigenschaften.get('zaehlbar', False):
            dict_verfuegbar[m.id] = m.Eigenschaften.get('anzahl', 1)
        else:
            dict_verfuegbar[m.id] = True
        for a in ausleihen:
            if int(m.id) in [int(x) for x in a.materialien.split(",") if x.isdigit()]:
                if a.ts_von <= date.today() <= a.ts_bis:
                    if m.Eigenschaften.get('zaehlbar', False) == False:
                        dict_verfuegbar[m.id] = False
                    else:
                        dict_verfuegbar[m.id] = dict_verfuegbar[m.id] - 1
    return dict_verfuegbar


def get_ausleihen_fuer_material(materialien: list[Material] | str) -> list:
    """Abfrage nach den Ausleihen in der Datenbank, die bestimmte Materialien
    enthalten

    Args:
        materialien (list[Material] | str): Liste von Material-Klassen oder einzelne id

    Returns:
        list: Enthält ein Tupel für jedes Material: z. B. 
        [(<Material 1>, [<Ausleihe 1>, <Ausleihe 2>]), (<Material 2>, [<Ausleihe 1>]),
    """
    if isinstance(materialien, str):
        materialien = Material.filter_by(id=materialien)
    elif not isinstance(materialien, list):
        return None
    ausleihen = [(a, a.materialien.split(",")) for a in Ausleihe.get_all()]
    if ausleihen == []:
        return None
    result = {m.id: [a[0] for a in ausleihen if str(
        m.id) in a[1]] for m in materialien}
    return result


def allowed_file(filename):
    """Test if uploaded images have legit filenames, Used by Auslagen
    image upload.

    Args:
        filename (str): Filename to be tested

    Returns:
        bool: True if filename is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["png", "jpg", "jpeg", "gif"]
