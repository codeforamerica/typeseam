# -*- coding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'auth', __name__,
    template_folder='../templates'
)
