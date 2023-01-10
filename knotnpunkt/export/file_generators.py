import json
import os
from datetime import datetime as dt
from pathlib import Path
from io import BytesIO
import cairosvg
from flask_login import current_user
from jinja2 import (
    Environment,
    FileSystemLoader,
)
import segno
from .._version import __version__
from ..database.db import (
    Material,
)


class ExportError(Exception):
    """Raised when something concerning export goes wrong
    """
    pass


class SVGGenerator():

    def __init__(self):
        try:
            self.config = json.load(open(Path(os.getcwd())/"knotnpunkt/export/export_templates.json"))
        except FileNotFoundError:
            raise ExportError("Konfigurationsdatei konnte nicht geladen werden.")
        self.jenv = Environment(loader=FileSystemLoader(Path(os.getcwd())/"knotnpunkt/export/export_templates"))

    def generate_svg(self, artikel: list[Material] = None, template_id: int = None) -> str:
        """Generiert eine SVG-Datei von einer bestimmten Vorlage mit bestimmtem
        Artikeln.

        Args:
            artikel (list[Material], optional): zu exportierende Materialien
            template_id (int, optional): Templatenummer laut export_templates.json

        Raises:
            ExportError

        Returns:
            str: Generierte SVg-Grafik
        """
        if template_id is None:
            template_id = self.standard_id
        if template_id not in self.all_templates.keys():
            raise ExportError("Angegebene Template-ID existiert nicht.")
        if len(artikel) > self.max_n_artikel(template_id):
            msg = f"Auf die angegeben Vorlage passen nur {self.max_n_artikel(template_id)} der {len(artikel)} Einträge."
            raise ExportError(msg)
        for m in artikel:
                code_string = f"knotnpunkt{__version__}:/{m.Kategorie.name}/{m.idMaterial}/\nName: {m.name}\nQR-Code erstellt: {dt.now():%d.%m.%Y %R}\nVon {current_user.name} ({current_user.benutzername})"
                code_string = code_string + " " * (130 - len(code_string))
                m.qrcode = segno.make(content=code_string, micro=False).svg_inline(scale=3.2)
        template_info = self.all_templates.get(template_id)
        template = self.jenv.get_template(template_info.get("dateiname"))
        return template.render(username=current_user.name, dt=dt, material_liste=artikel, org_name="DPSG Beckum", host_info=f"knotnpunkt version {__version__}")

    @property
    def standard_id(self):
        return self.config.get("standard_id", None)

    @property
    def default_templates(self):
        return {t["id"]: t for t in self.config.get("default_templates")}

    @property
    def custom_templates(self):
        return {t["id"]: t for t in self.config.get("custom_templates")}

    @property
    def all_templates(self):
        return {**self.default_templates, **self.custom_templates}

    def max_n_artikel(self, template_id: int) -> int:
        """Return Maximum number of items per page for given template id

        Args:
            template_id (int): Template ID to look up

        Returns:
            int: Config-defined maximum item number
        """
        return self.all_templates.get(template_id).get('artikel_pro_seite')


class PDFGenerator(SVGGenerator):

    def generate_pdf(self, artikel: list[Material] = None, template_id: int = None) -> BytesIO:
        """Generiere eine PDF-DAtei anstelle von SVG

        Args:
            artikel (list[Material], optional): s. generate_svg(...). Defaults to None.
            template_id (int, optional): s. generate_svg(...). Defaults to None.

        Returns:
            BytesIO: PDF-Datei als BytesIO-Buffer
        """
        svg = self.generate_svg(artikel=artikel, template_id=template_id)
        pdf = cairosvg.svg2pdf(bytestring=svg.encode("utf-8"))
        return BytesIO(pdf)
