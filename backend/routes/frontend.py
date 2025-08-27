#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frontend serving routes
"""

from flask import Blueprint, send_from_directory, render_template_string
import os
import logging

logger = logging.getLogger(__name__)

# Kreiranje Blueprint-a za frontend routes
frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """Serviraj glavni HTML fajl."""
    try:
        # Definiši apsolutnu putanju do template fajla
        template_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'templates', 'index.html')
        template_path = os.path.abspath(template_path)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace Flask template syntax with static paths for Electron
        html_content = html_content.replace(
            "{{ url_for('static', filename='css/style.css') }}", 
            "/static/css/style.css"
        )
        html_content = html_content.replace(
            "{{ url_for('static', filename='js/app.js') }}", 
            "/static/js/app.js"
        )
        
        return render_template_string(html_content)
    except Exception as e:
        logger.error(f"Greška pri učitavanju index.html: {e}")
        return f"Greška pri učitavanju aplikacije: {e}", 500

@frontend_bp.route('/static/<path:filename>')
def static_files(filename):
    """Serviraj statičke fajlove."""
    static_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static')
    static_path = os.path.abspath(static_path)
    return send_from_directory(static_path, filename)
