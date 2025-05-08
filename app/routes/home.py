from flask import Blueprint, render_template, redirect, url_for
from app.utils.session_manager import initialize_brand_parameters, get_input_methods

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    # Initialize brand parameters in session
    initialize_brand_parameters()
    
    # Get input methods status
    input_methods = get_input_methods()
    
    return render_template('home/index.html', input_methods=input_methods)
