import humanize as hu
from sqlalchemy import desc
import json
from datetime import datetime as dt
from datetime import date
from .database.db import (
    Ausleihe,
    Material,
)


def convertTime(datetime):
    _t = hu.i18n.activate("de_DE")
    return hu.naturaltime(dt.now()-dt.strptime(datetime.get('zuletztGescannt'), '%Y-%m-%d %H:%M'))


def checkverfuegbarkeit(materialien):
    dict_verfuegbar = {}
    ausleihen = Ausleihe.query.order_by(desc(Ausleihe.ts_von)).all()
    for m in materialien:
        if m.Eigenschaften.get('zaehlbar', False):
            dict_verfuegbar[m.idMaterial] = m.Eigenschaften.get('anzahl', 1)
        else:
            dict_verfuegbar[m.idMaterial] = True
        for a in ausleihen:
            if int(m.idMaterial) in [int(x) for x in a.materialien.split(",")]:
                if a.ts_von <= date.today() <= a.ts_bis:
                    if m.Eigenschaften.get('zaehlbar', False) == False:
                        dict_verfuegbar[m.idMaterial] = False
                    else:
                        dict_verfuegbar[m.idMaterial] = dict_verfuegbar[m.idMaterial] - 1
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
        materialien = Material.query.filter_by(idMaterial=material).all()
    elif not isinstance(materialien, list):
        return None
    ausleihen = [(a, a.materialien.split(",")) for a in Ausleihe.query.all()]
    if ausleihen == []:
        return None
    result = {m.idMaterial: [a[0] for a in ausleihen if str(
        m.idMaterial) in a[1]] for m in materialien}
    return result
