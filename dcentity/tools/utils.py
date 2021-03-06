import os

from django.contrib.localflavor.us.us_states import STATE_CHOICES

def fix_dict_keys(unicode_dict):
    return dict((str(k), v) for k,v in unicode_dict.iteritems())

# Dict mapping state abbreviations to full state names
EXPAND_STATES = dict(STATE_CHOICES)
def expand_state(state):
    return EXPAND_STATES.get(state, state)

class reopen_csv_writer:
    """
    `with` statement helper to read the contents of a CSV file,
    then reopen it in 'append' mode.  Usage:

        with open(filename) as (rows, writer):
            ...
    """

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self, *args, **kwargs):
        rows = []
        if os.path.exists(self.filename):
            with open(self.filename) as fh:
                reader = UnicodeReader(fh)
                rows = [r for r in reader]
        self.fh = open(self.filename, 'a')
        writer = UnicodeWriter(self.fh)
        return (rows, writer)

    def __exit__(self, *args, **kwargs):
        self.fh.close()

# The following taken from python standard library docs for unicode CSV writing
# and reading:
import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

def path_relative_to(relative_to, *args):
    return os.path.abspath(os.path.join(*((os.path.dirname(relative_to),) + args)))

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") if hasattr(s, 'encode') else s for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
