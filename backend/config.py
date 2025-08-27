#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for MIDI Configurator Backend
"""

import os
import logging

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Logging configuration
LOG_LEVEL = logging.INFO

# Server configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001
DEBUG_MODE = True

# Paths configuration
FRONTEND_STATIC_PATH = '../frontend/static'
FRONTEND_TEMPLATES_PATH = '../frontend/templates'

# Logging setup
def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()
