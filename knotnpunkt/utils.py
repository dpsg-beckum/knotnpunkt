import humanize as hu
from sqlalchemy import desc
import json
from datetime import datetime as dt
from datetime import date
from .database.db import (
    Ausleihe
)


def convertTime(datetime):
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

