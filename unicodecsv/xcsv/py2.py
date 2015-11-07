# -*- coding: utf-8 -*-
from __future__ import unicode_literals


__all__ = [ "QUOTE_MINIMAL", "QUOTE_ALL", "QUOTE_NONNUMERIC", "QUOTE_NONE",
            "Error", "Dialect", "__doc__", "excel", "excel_tab",
            "field_size_limit", "reader", "writer",
            "register_dialect", "get_dialect", "list_dialects", "Sniffer",
            "unregister_dialect", "__version__", "DictReader", "DictWriter" ]

import csv
from csv import (
    QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE,
    __version__, __doc__, Error, field_size_limit, Sniffer,
)

def extend_dialect(dialect, **fmtparams):
    """Make a new class with the fmtparams overridden."""
    return type(str('ExtendedDialect'), (dialect,), dict(fmtparams))


class writer(object):
    def __init__(self, fileobj, dialect='excel', **fmtparams):
        self.fileobj = fileobj
        base_dialect = get_dialect(dialect)
        dialect_class = extend_dialect(base_dialect, **fmtparams)
        self.dialect = dialect_class()

    def writerow(self, row):
        line = self.dialect.delimiter.join(row) + self.dialect.lineterminator
        self.fileobj.write(line)


class reader(object):
    def __init__(self, fileobj, dialect='excel', **fmtparams):
        self.fileobj = iter(fileobj)
        base_dialect = get_dialect(dialect)
        dialect_class = extend_dialect(base_dialect, **fmtparams)
        self.dialect = dialect_class()

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.fileobj)
        if line.endswith(self.dialect.lineterminator):
            line = line[:-(len(self.dialect.lineterminator))]
        return line.split(self.dialect.delimiter)

    next = __next__


class DictReader(object):
    pass


class DictWriter(object):
    pass


_dialect_registry = {}
def register_dialect(name, dialect):
    assert name not in _dialect_registry
    _dialect_registry[name] = dialect

def unregister_dialect(name):
    _dialect_registery.pop(name)

def get_dialect(name):
    return _dialect_registry[name]

def list_dialects():
    return list(_dialect_registry)


class Dialect(object):
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
