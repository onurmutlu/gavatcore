#!/usr/bin/env python3
"""
Basit logger adaptörü: get_logger(name) -> structlog logger
Bu modül, eski "infrastructure.config.logger" import'larını karşılamak içindir.
"""

import structlog


def get_logger(name: str):
    return structlog.get_logger(name)
