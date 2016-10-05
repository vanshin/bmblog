# -*- coding: UTF-8 -*-
from flask import Blueprint
from ..models import Permission

main = Blueprint('main',__name__)

from . import view, error

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
