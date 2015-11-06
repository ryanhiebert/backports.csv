# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
from csv import (
    QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE,
    __version__, __doc__, Error, field_size_limit, Sniffer,
)


def writer():
    pass

def reader():
    pass

class DictReader():
    pass

class DictWriter():
    pass


_dialect_registry = {}
def register_dialect(name, dialect):
    assert name not in _dialect_registry
    _dialect_registry[name] = dialect

def unregister_dialect(name):
    _dialect_registery.pop(name)

def get_dialect(name):
    _dialect_registry[name]

def list_dialects():
    return list(_dialect_registry)


class Dialect:
    """Describe a CSV dialect.
    This must be subclassed (see csv.excel).  Valid attributes are:
    delimiter, quotechar, escapechar, doublequote, skipinitialspace,
    lineterminator, quoting.
    """
    _name = ""
    _valid = False
    # placeholders
    delimiter = None
    quotechar = None
    escapechar = None
    doublequote = None
    skipinitialspace = None
    lineterminator = None
    quoting = None

    def __init__(self):
        if self.__class__ != Dialect:
            self._valid = True


class excel(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("excel", excel)

class excel_tab(excel):
    """Describe the usual properties of Excel-generated TAB-delimited files."""
    delimiter = '\t'
register_dialect("excel-tab", excel_tab)

class unix_dialect(Dialect):
    """Describe the usual properties of Unix-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = QUOTE_ALL
register_dialect("unix", unix_dialect)
