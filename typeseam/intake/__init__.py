# -*- coding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'intake', __name__, url_prefix='/intake',
    template_folder='../templates'
)

from . import views