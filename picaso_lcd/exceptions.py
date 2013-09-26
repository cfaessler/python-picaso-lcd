# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

class PicasoError(RuntimeError):
    """Something went wrong while processing the command."""

class CommunicationError(RuntimeError):
    """Communication with device failed (e.g. a serial read / write timeout)."""
