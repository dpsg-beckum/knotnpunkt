import base64
import json
from datetime import datetime as dt
from pathlib import Path
from io import BytesIO
import cairosvg
from flask import current_app
from flask_login import current_user
from jinja2 import (
    Environment,
    FileSystemLoader,
)
import segno
from segno.helpers import make_epc_qr
from .._version import __version__
from ..database.db import (
    Material,
    Auslage,
    AuslagenKategorie,
)


class ExportError(Exception):
    """Raised when something concerning export goes wrong
    """
    pass


class SVGGenerator():

    def __init__(self):
        try:
            self.config = json.load(open(Path(current_app.root_path)/"export/export_templates.json"))
        except FileNotFoundError:
            raise ExportError("Konfigurationsdatei konnte nicht geladen werden.")
        self.jenv = Environment(loader=FileSystemLoader(Path(current_app.root_path)/"export/export_templates"))
        self.jenv.filters['b64encode'] = base64.b64encode

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


class AuslagenSVGGenerator(SVGGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_svg(self, auslage: Auslage = None, template_id: int = None) -> str:
        """Generiert eine SVG-Datei von einer Auslage

        Args:
            auslage (Auslage): zu exportierende Auslage
            template_id (int, optional): Templatenummer laut export_templates.json

        Raises:
            ExportError

        Returns:
            str: Generierte SVg-Grafik
        """
        if template_id is None:
            raise ExportError("Für Auslagen gibt es kein Standard-Template")
        if template_id not in self.all_templates.keys():
            raise ExportError("Angegebene Template-ID existiert nicht.")
        # If config is set, include a EPC QR-Code in the output
        if current_app.config.get("KP_GIROCODE", True):
            auslage.qrcode = make_epc_qr(name=auslage.kontoinhaber,
                                         iban=auslage.iban,
                                         amount=auslage.betrag,
                                         text=f'Rückerstattung: "{auslage.titel}" automatisch generiert von Auslagen-ID #{auslage.idAuslage}').svg_inline(scale=0.6)
        template_info = self.all_templates.get(template_id)
        template = self.jenv.get_template(template_info.get("dateiname"))
        return template.render(item=auslage, org_name="DPSG Beckum", host_info="", version=__version__, dt=dt, current_benutzername=current_user.benutzername)


class AuslagenPDFGenerator(AuslagenSVGGenerator):

    def generate_pdf(self, auslage: Auslage = None, template_id: int = None) -> BytesIO:
        """Generiere eine PDF-DAtei anstelle von SVG

        Args:
            auslage (Auslage): s. generate_svg(...). Defaults to None.
            template_id (int, optional): s. generate_svg(...). Defaults to None.

        Returns:
            BytesIO: PDF-Datei als BytesIO-Objekt
        """
        svg = self.generate_svg(auslage=auslage, template_id=template_id)
        # The unsafe-flag is mandatory to embed base64 images
        pdf = cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), unsafe=True)
        return BytesIO(pdf)
