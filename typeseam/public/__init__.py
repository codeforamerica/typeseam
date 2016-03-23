# -*- coding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'public', __name__,
    template_folder='../templates'
)

from . import views