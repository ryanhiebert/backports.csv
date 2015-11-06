# -*- coding: utf-8 -*-
"""A port of Python 3's csv module to Python 2.

The API of the csv module in Python 2 is drastically different from the
the csv module in Python 3. This is due for the most part to the
difference between str in Python 2 and Python 3.

The semantics of Python 3's version aremore useful because they support
unicode natively, while Python 2's csv does not.
"""
import sys

if sys.version_info >= (3, 0):
    from csv import *
else:
    from unicodecsv.xcsv.py2 import *
