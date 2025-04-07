import base64

from flask import Blueprint, Response, abort, request, send_file
from flask_login import login_required

from .._version import __version__
from ..database.json_encoder import DatabaseEncoder
from ..database.material import Img
from ..export.file_generators import ExportError, PDFGenerator, SVGGenerator
from ..utils import get_ausleihen_fuer_material

img_route = Blueprint("img", __name__, url_prefix="/img")


@img_route.before_request
@login_required
def auth():
    pass


@img_route.route('/<int:id>')
def get_img(id: int):
    img = Img.get_via_id(id)
    return Response(img.img, mimetype='image/png')
