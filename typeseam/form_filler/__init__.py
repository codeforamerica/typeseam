# -*- coding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'form_filler', __name__,
    template_folder='../templates'
)

from . import views
