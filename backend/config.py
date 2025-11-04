#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for MIDI Configurator Backend
"""

import os
import sys
import logging

# Base path resolution (supports PyInstaller and packaged Electron)
_BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(__file__))

# Database configuration (defaults next to backend; consider moving to userData for persistence)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Logging configuration
LOG_LEVEL = logging.INFO

# Server configuration
SERVER_HOST = os.environ.get('BACKEND_HOST', '127.0.0.1')
SERVER_PORT = int(os.environ.get('BACKEND_PORT', '5001'))
DEBUG_MODE = os.environ.get('BACKEND_DEBUG', '1') == '1'

# Paths configuration
_ENV_FRONTEND_DIR = os.environ.get('FRONTEND_DIR')
if _ENV_FRONTEND_DIR:
    FRONTEND_STATIC_PATH = os.path.join(_ENV_FRONTEND_DIR, 'static')
    FRONTEND_TEMPLATES_PATH = os.path.join(_ENV_FRONTEND_DIR, 'templates')
else:
    # Fallback to relative paths (development)
    FRONTEND_STATIC_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
    FRONTEND_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')

# Logging setup
def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()
