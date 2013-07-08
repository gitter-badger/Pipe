# -*- coding: utf8 -*-
'''
@project   Maprox <http://www.maprox.net>
@info      Teltonika FMXXXX firmware
@copyright 2009-2013, Maprox LLC
'''

from lib.handlers.teltonika.abstract import TeltonikaHandler

class Handler(TeltonikaHandler):
    """ Teltonika. FMXXXX """
    pass


# ===========================================================================
# TESTS
# ===========================================================================

import unittest
from lib.ip import get_ip
class TestCase(unittest.TestCase):

    def setUp(self):
        pass
