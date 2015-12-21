# -*- coding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'intake', __name__,
    template_folder='../templates'
)

from . import views