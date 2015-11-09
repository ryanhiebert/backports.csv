# -*- coding: utf-8 -*-
from __future__ import unicode_literals


__all__ = [ "QUOTE_MINIMAL", "QUOTE_ALL", "QUOTE_NONNUMERIC", "QUOTE_NONE",
            "Error", "Dialect", "__doc__", "excel", "excel_tab",
            "field_size_limit", "reader", "writer",
            "register_dialect", "get_dialect", "list_dialects", "Sniffer",
            "unregister_dialect", "__version__", "DictReader", "DictWriter" ]

import re
from io import StringIO
from csv import (
    QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE,
    __version__, __doc__, Error, field_size_limit,
)

# Stuff needed from six
import sys
PY3 = sys.version_info[0] == 3
string_types = str if PY3 else basestring
text_type = str if PY3 else unicode
binary_type = bytes if PY3 else str
unichr = chr if PY3 else unichr


class writer(object):
    def __init__(self, fileobj, dialect='excel', **fmtparams):
        self.fileobj = fileobj
        self.dialect = Dialect.combine(dialect, fmtparams)

    def prepfield(self, field):
        return text_type(field)

    def writerow(self, row):
        row = [self.prepfield(field) for field in row]
        line = self.dialect.delimiter.join(row) + self.dialect.lineterminator
        self.fileobj.write(line)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class reader(object):
    def __init__(self, fileobj, dialect='excel', **fmtparams):
        self.fileobj = iter(fileobj)
        self.dialect = Dialect.combine(dialect, fmtparams)
        self.line_num = 0

    def __iter__(self):
        return self

    def __next__(self):
        lineterminators = ['\r\n', '\r', '\n']
        line = '\n'
        while line in lineterminators:
            line = next(self.fileobj)

        for lineterminator in lineterminators:
            if line.endswith(lineterminator):
                line = line[:-len(lineterminator)]
                break

        self.line_num += 1
        fields = line.split(self.dialect.delimiter)

        limit = field_size_limit()
        if any(len(field) > limit for field in fields):
            raise Error('Field is too long')

        return fields

    next = __next__


_dialect_registry = {}
def register_dialect(name, dialect=None, **fmtparams):
    if not isinstance(name, text_type):
        raise TypeError('"name" must be a string')

    dialect = Dialect.extend(dialect, fmtparams)

    try:
        Dialect.validate(dialect)
    except:
        raise TypeError('dialect is invalid')

    assert name not in _dialect_registry
    _dialect_registry[name] = dialect

def unregister_dialect(name):
    try:
        _dialect_registry.pop(name)
    except KeyError:
        raise Error('"{name}" not a registered dialect'.format(name=name))

def get_dialect(name):
    try:
        return _dialect_registry[name]
    except KeyError:
        raise Error('Could not find dialect {0}'.format(name))

def list_dialects():
    return list(_dialect_registry)


class Dialect(object):
    """Describe a CSV dialect.
    This must be subclassed (see csv.excel).  Valid attributes are:
    delimiter, quotechar, escapechar, doublequote, skipinitialspace,
    lineterminator, quoting, strict.
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
    strict = None

    def __init__(self):
        self.validate(self)
        if self.__class__ != Dialect:
            self._valid = True

    @classmethod
    def validate(cls, dialect):
        dialect = cls.extend(dialect)

        if not isinstance(dialect.quoting, int):
            raise Error('"quoting" must be an integer')

        if dialect.delimiter is None:
            raise Error('delimiter must be set')
        cls.validate_text(dialect, 'delimiter')

        if dialect.lineterminator is None:
            raise Error('lineterminator must be set')
        if not isinstance(dialect.lineterminator, text_type):
            raise Error('"lineterminator" must be a string')

        if dialect.quoting != QUOTE_NONE:
            if dialect.quotechar is None:
                raise Error('quotechar must be set if quoting enabled')
            cls.validate_text(dialect, 'quotechar')

    @staticmethod
    def validate_text(dialect, attr):
        val = getattr(dialect, attr)
        if not isinstance(val, text_type):
            if type(val) == bytes:
                raise Error('"{0}" must be string, not bytes'.format(attr))
            raise Error('"{0}" must be string, not {1}'.format(
                attr, type(val).__name__))

        if len(val) != 1:
            raise Error('"{0}" must be a 1-character string'.format(attr))

    @staticmethod
    def defaults():
        return {
            'delimiter': ',',
            'doublequote': True,
            'escapechar': None,
            'lineterminator': '\r\n',
            'quotechar': '"',
            'quoting': QUOTE_MINIMAL,
            'skipinitialspace': False,
            'strict': False, 
        }

    @classmethod
    def extend(cls, dialect, fmtparams=None):
        if isinstance(dialect, string_types):
            dialect = get_dialect(dialect)

        if fmtparams is None:
            return dialect

        defaults = cls.defaults()

        if any(param not in defaults for param in fmtparams):
            raise TypeError('Invalid fmtparam')

        specified = dict(
            (attr, getattr(dialect, attr, None))
            for attr in cls.defaults()
        )

        specified.update(fmtparams)
        return type(str('ExtendedDialect'), (cls,), specified)

    @classmethod
    def combine(cls, dialect, fmtparams):
        """Create a new dialect with defaults and added parameters."""
        dialect = cls.extend(dialect, fmtparams)
        defaults = cls.defaults()
        specified = dict(
            (attr, getattr(dialect, attr, None))
            for attr in defaults
            if getattr(dialect, attr, None) is not None
        )

        defaults.update(specified)
        dialect = type(str('CombinedDialect'), (cls,), defaults)
        cls.validate(dialect)
        return dialect


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


class DictReader:
    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect="excel", *args, **kwds):
        self._fieldnames = fieldnames   # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.reader = reader(f, dialect, *args, **kwds)
        self.dialect = dialect
        self.line_num = 0

    def __iter__(self):
        return self

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = next(self.reader)
            except StopIteration:
                pass
        self.line_num = self.reader.line_num
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    def __next__(self):
        if self.line_num == 0:
            # Used only for its side effect.
            self.fieldnames
        row = next(self.reader)
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = next(self.reader)
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d

    next = __next__


class DictWriter:
    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="excel", *args, **kwds):
        self.fieldnames = fieldnames    # list of keys for the dict
        self.restval = restval          # for writing short dicts
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError("extrasaction (%s) must be 'raise' or 'ignore'"
                             % extrasaction)
        self.extrasaction = extrasaction
        self.writer = writer(f, dialect, *args, **kwds)

    def writeheader(self):
        header = dict(zip(self.fieldnames, self.fieldnames))
        self.writerow(header)

    def _dict_to_list(self, rowdict):
        if self.extrasaction == "raise":
            wrong_fields = [k for k in rowdict if k not in self.fieldnames]
            if wrong_fields:
                raise ValueError("dict contains fields not in fieldnames: "
                                 + ", ".join([repr(x) for x in wrong_fields]))
        return (rowdict.get(key, self.restval) for key in self.fieldnames)

    def writerow(self, rowdict):
        return self.writer.writerow(self._dict_to_list(rowdict))

    def writerows(self, rowdicts):
        return self.writer.writerows(map(self._dict_to_list, rowdicts))

# Guard Sniffer's type checking against builds that exclude complex()
try:
    complex
except NameError:
    complex = float

class Sniffer:
    '''
    "Sniffs" the format of a CSV file (i.e. delimiter, quotechar)
    Returns a Dialect object.
    '''
    def __init__(self):
        # in case there is more than one possible delimiter
        self.preferred = [',', '\t', ';', ' ', ':']


    def sniff(self, sample, delimiters=None):
        """
        Returns a dialect (or None) corresponding to the sample
        """

        quotechar, doublequote, delimiter, skipinitialspace = \
                   self._guess_quote_and_delimiter(sample, delimiters)
        if not delimiter:
            delimiter, skipinitialspace = self._guess_delimiter(sample,
                                                                delimiters)

        if not delimiter:
            raise Error("Could not determine delimiter")

        class dialect(Dialect):
            _name = "sniffed"
            lineterminator = '\r\n'
            quoting = QUOTE_MINIMAL
            # escapechar = ''

        dialect.doublequote = doublequote
        dialect.delimiter = delimiter
        # _csv.reader won't accept a quotechar of ''
        dialect.quotechar = quotechar or '"'
        dialect.skipinitialspace = skipinitialspace

        return dialect


    def _guess_quote_and_delimiter(self, data, delimiters):
        """
        Looks for text enclosed between two identical quotes
        (the probable quotechar) which are preceded and followed
        by the same character (the probable delimiter).
        For example:
                         ,'some text',
        The quote with the most wins, same with the delimiter.
        If there is no quotechar the delimiter can't be determined
        this way.
        """

        matches = []
        for restr in ('(?P<delim>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?P=delim)', # ,".*?",
                      '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?P<delim>[^\w\n"\'])(?P<space> ?)',   #  ".*?",
                      '(?P<delim>>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?:$|\n)',  # ,".*?"
                      '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?:$|\n)'):                            #  ".*?" (no delim, no space)
            regexp = re.compile(restr, re.DOTALL | re.MULTILINE)
            matches = regexp.findall(data)
            if matches:
                break

        if not matches:
            # (quotechar, doublequote, delimiter, skipinitialspace)
            return ('', False, None, 0)
        quotes = {}
        delims = {}
        spaces = 0
        groupindex = regexp.groupindex
        for m in matches:
            n = groupindex['quote'] - 1
            key = m[n]
            if key:
                quotes[key] = quotes.get(key, 0) + 1
            try:
                n = groupindex['delim'] - 1
                key = m[n]
            except KeyError:
                continue
            if key and (delimiters is None or key in delimiters):
                delims[key] = delims.get(key, 0) + 1
            try:
                n = groupindex['space'] - 1
            except KeyError:
                continue
            if m[n]:
                spaces += 1

        quotechar = max(quotes, key=quotes.get)

        if delims:
            delim = max(delims, key=delims.get)
            skipinitialspace = delims[delim] == spaces
            if delim == '\n': # most likely a file with a single column
                delim = ''
        else:
            # there is *no* delimiter, it's a single column of quoted data
            delim = ''
            skipinitialspace = 0

        # if we see an extra quote between delimiters, we've got a
        # double quoted format
        dq_regexp = re.compile(
                               r"((%(delim)s)|^)\W*%(quote)s[^%(delim)s\n]*%(quote)s[^%(delim)s\n]*%(quote)s\W*((%(delim)s)|$)" % \
                               {'delim':re.escape(delim), 'quote':quotechar}, re.MULTILINE)



        if dq_regexp.search(data):
            doublequote = True
        else:
            doublequote = False

        return (quotechar, doublequote, delim, skipinitialspace)


    def _guess_delimiter(self, data, delimiters):
        """
        The delimiter /should/ occur the same number of times on
        each row. However, due to malformed data, it may not. We don't want
        an all or nothing approach, so we allow for small variations in this
        number.
          1) build a table of the frequency of each character on every line.
          2) build a table of frequencies of this frequency (meta-frequency?),
             e.g.  'x occurred 5 times in 10 rows, 6 times in 1000 rows,
             7 times in 2 rows'
          3) use the mode of the meta-frequency to determine the /expected/
             frequency for that character
          4) find out how often the character actually meets that goal
          5) the character that best meets its goal is the delimiter
        For performance reasons, the data is evaluated in chunks, so it can
        try and evaluate the smallest portion of the data possible, evaluating
        additional chunks as necessary.
        """

        data = list(filter(None, data.split('\n')))

        ascii = [unichr(c) for c in range(127)] # 7-bit ASCII

        # build frequency tables
        chunkLength = min(10, len(data))
        iteration = 0
        charFrequency = {}
        modes = {}
        delims = {}
        start, end = 0, min(chunkLength, len(data))
        while start < len(data):
            iteration += 1
            for line in data[start:end]:
                for char in ascii:
                    metaFrequency = charFrequency.get(char, {})
                    # must count even if frequency is 0
                    freq = line.count(char)
                    # value is the mode
                    metaFrequency[freq] = metaFrequency.get(freq, 0) + 1
                    charFrequency[char] = metaFrequency

            for char in charFrequency.keys():
                items = list(charFrequency[char].items())
                if len(items) == 1 and items[0][0] == 0:
                    continue
                # get the mode of the frequencies
                if len(items) > 1:
                    modes[char] = max(items, key=lambda x: x[1])
                    # adjust the mode - subtract the sum of all
                    # other frequencies
                    items.remove(modes[char])
                    modes[char] = (modes[char][0], modes[char][1]
                                   - sum(item[1] for item in items))
                else:
                    modes[char] = items[0]

            # build a list of possible delimiters
            modeList = modes.items()
            total = float(chunkLength * iteration)
            # (rows of consistent data) / (number of rows) = 100%
            consistency = 1.0
            # minimum consistency threshold
            threshold = 0.9
            while len(delims) == 0 and consistency >= threshold:
                for k, v in modeList:
                    if v[0] > 0 and v[1] > 0:
                        if ((v[1]/total) >= consistency and
                            (delimiters is None or k in delimiters)):
                            delims[k] = v
                consistency -= 0.01

            if len(delims) == 1:
                delim = list(delims.keys())[0]
                skipinitialspace = (data[0].count(delim) ==
                                    data[0].count("%c " % delim))
                return (delim, skipinitialspace)

            # analyze another chunkLength lines
            start = end
            end += chunkLength

        if not delims:
            return ('', 0)

        # if there's more than one, fall back to a 'preferred' list
        if len(delims) > 1:
            for d in self.preferred:
                if d in delims.keys():
                    skipinitialspace = (data[0].count(d) ==
                                        data[0].count("%c " % d))
                    return (d, skipinitialspace)

        # nothing else indicates a preference, pick the character that
        # dominates(?)
        items = [(v,k) for (k,v) in delims.items()]
        items.sort()
        delim = items[-1][1]

        skipinitialspace = (data[0].count(delim) ==
                            data[0].count("%c " % delim))
        return (delim, skipinitialspace)


    def has_header(self, sample):
        # Creates a dictionary of types of data in each column. If any
        # column is of a single type (say, integers), *except* for the first
        # row, then the first row is presumed to be labels. If the type
        # can't be determined, it is assumed to be a string in which case
        # the length of the string is the determining factor: if all of the
        # rows except for the first are the same length, it's a header.
        # Finally, a 'vote' is taken at the end for each column, adding or
        # subtracting from the likelihood of the first row being a header.

        rdr = reader(StringIO(sample), self.sniff(sample))

        header = next(rdr) # assume first row is header

        columns = len(header)
        columnTypes = {}
        for i in range(columns): columnTypes[i] = None

        checked = 0
        for row in rdr:
            # arbitrary number of rows to check, to keep it sane
            if checked > 20:
                break
            checked += 1

            if len(row) != columns:
                continue # skip rows that have irregular number of columns

            for col in list(columnTypes.keys()):

                for thisType in [int, float, complex]:
                    try:
                        thisType(row[col])
                        break
                    except (ValueError, OverflowError):
                        pass
                else:
                    # fallback to length of string
                    thisType = len(row[col])

                if thisType != columnTypes[col]:
                    if columnTypes[col] is None: # add new column type
                        columnTypes[col] = thisType
                    else:
                        # type is inconsistent, remove column from
                        # consideration
                        del columnTypes[col]

        # finally, compare results against first row and "vote"
        # on whether it's a header
        hasHeader = 0
        for col, colType in columnTypes.items():
            if type(colType) == type(0): # it's a length
                if len(header[col]) != colType:
                    hasHeader += 1
                else:
                    hasHeader -= 1
            else: # attempt typecast
                try:
                    colType(header[col])
                except (ValueError, TypeError):
                    hasHeader += 1
                else:
                    hasHeader -= 1

        return hasHeader > 0
