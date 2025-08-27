#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error handlers for the Flask application
"""

from flask import jsonify

def register_error_handlers(app):
    """Registruj error handlers za Flask aplikaciju."""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
