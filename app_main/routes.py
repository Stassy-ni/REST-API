from flask import Blueprint, jsonify
from .models import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({"message": "Main service OK"})
