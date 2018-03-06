import os

from datetime import datetime, timedelta
from collections import defaultdict

import lxml.html


class Report:
    """Class that represents report file

    Attributes
    ----------
    path : str
        System path to a report file.
    data : list
        Raw, unprocessed, 3 columns of useful data parsed from report.
    name : str
        File name extracted from file path.
    date : datetime
        datetime obj, representing date report was generated.
    """

    def __init__(self, path):
        self.path = path
        self.data = list(parse(self.path))
        self.name_from_path()
        self.date_from_name()
        self.sum_data()

    @property
    def date_as_string(self):
        """str : String representation of datetime object"""
        return datetime.strftime(self.date, '%Y-%m-%d')

    @property
    def idle_time(self):
        """timedelta : Returns the time laser was in idle"""
        return self.summary.get('idle')

    @property
    def busy_time(self):
        """timedelta : Returns the time laser was in work"""
        values = [self.summary[key] for key in self.summary if key != 'idle']
        return sum(values, timedelta())

    @property
    def jobs(self):
        """dict : Returns parsed programs"""
        return {k: v for k, v in self.summary.items() if k != 'idle'}

    def items(self):
        """Simple addapter to dict .items() method"""
        return self.summary.items()

    def name_from_path(self):
        """Set self.name extracted from report's name"""
        self.name = os.path.split(self.path)[1]

    def date_from_name(self):
        """Set self.date extracted from report's name"""
        date = [int(x) for x in os.path.splitext(self.name)[0].split('_')]
        self.date = datetime(*date)

    def sum_data(self):
        """Summarize parsed data

        Explanation of algorithm:
        +----------+------+---------+
        |   Time   | Name | Status  |
        +----------+------+---------+
        | 00:00:00 | prg1 | STARTED |
        | 01:00:00 | prg1 | STOPPED |
        | 01:05:00 | prg2 | STARTED |
        | 02:05:00 | prg2 | STOPPED |
        | 02:10:00 | prg3 | STARTED |
        | 03:10:00 | prg3 | STOPPED |
        +----------+------+---------+
        Each report reprsent the working day.
        Time in first column is timedelta objects.

        At each iteration we need to determine how much time the program was in
        work or laser was off work, time interval between two statuses reprsent
        this time, whether program was in work (started->stopped) or laser
        was in idle (stopped->started).

        'current' - current time in "table", changes at each iteration.

        1st row. prg1 started, calculate how much time passed from previous
        stopped status (idle): 00:00:00 - current (which is 00:00:00),
        new current is 1st row "time" (00:00:00).

        2nd row. prg1 stopped, calculate how much time passed from started
        status: 01:00:00 - current, writes data to dict: {'prg1':01:00:00},
        New current is 2nd row "time" (01:00:00).

        Repeating the procces above until StopIteration raised we'll get:
        data = {'prg1': 01:00:00, 'prg2': 01:00:00, 'prg3': 01:00:00},
        current = 03:10:00 and idle equals to 00:10:00.

        As StopIteration raised we need to know which status was last, in case
        above it is "STOPPED", so we need to calculate how much time passed
        from the time in last row to the end of the day:
        24:00:00 - 03:10:00, idle + 20:50:00 which sums up to a total 21:00:00
        now: data = {'prg1': 01:00:00, 'prg2': 01:00:00, 'prg3': 01:00:00,
                     'idle': 21:00:00}

        In case where last status is STARTED we need to calculate how much time
        last program was in work till the day end and add it to results.
        """
        idle = timedelta()  # collects ammout of time laser wasn't working
        current = timedelta()  # used to determine current position in table
        data = defaultdict(timedelta)
        # Using manual iteration because we need to handle the end of iteration
        # and because I don't want to use for/else thing.
        i = iter(self.data)
        try:
            while True:
                # (00:00:00, prg1, STARTED)
                time, name, status = next(i)
                if status == 'STARTED':
                    idle += time - current
                    current = time
                else:
                    data[name] += time - current
                    current = time
        except StopIteration:
            if status == 'STARTED':
                data[name] += timedelta(days=1) - current
            else:
                idle += timedelta(days=1) - current
        data['idle'] += idle
        self.summary = data


def read_report(path):
    return Report(path)


def parse(path):
    """Extracts data wrapped in <tr> tags.

    Last 2 columns of report are not interesting and therefore omitted.

    Parameters
    ----------
    path : str
        Path to the report file.

    Yields
    ------
    tuple
        Tuple of 3 useful report's rows : time, name, status.
    """
    tree = lxml.html.parse(path).getroot()
    iterator = tree.iter('tr')
    next(iterator)  # skip headers
    for elem in iterator:
        time, name, status, *_ = elem
        yield convert_time(time.text), name.text, status.text


def convert_time(time):
    """Returns timedelta object converted from string.

    Parameters
    ----------
    time : str
        Time string.

    Returns
    -------
    timedelta
        timedelta object converted from string.

    Example
    -------
    >>> convert_time('10:11:12')
    datetime.timedelta(0, 36672)
    """
    time_string = time.split(':')
    return timedelta(hours=int(time_string[0]),
                     minutes=int(time_string[1]),
                     seconds=int(time_string[2])
                     )
