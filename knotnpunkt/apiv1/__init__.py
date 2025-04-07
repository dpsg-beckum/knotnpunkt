"""The api submodule contains routes that dont render templates.
"""

from flask import Blueprint

from ..database.exceptions import ElementDoesNotExsist
from .auslagen import auslagen_routes
from .img import img_route
from .material import materialBlueprint

apiv1 = Blueprint("apiv1", __name__, template_folder="templates",
                  url_prefix="/api/v1")

apiv1.register_blueprint(materialBlueprint)
apiv1.register_blueprint(img_route)
apiv1.register_blueprint(auslagen_routes)


@apiv1.errorhandler(ElementDoesNotExsist)
def handle_element_does_not_exist(error):
    return {"error": "Element does not exist"}, 404
