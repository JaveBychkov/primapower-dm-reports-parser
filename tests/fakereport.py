from datetime import timedelta
from io import StringIO
from itertools import cycle

from lxml.html import tostring
from lxml.html.builder import E


# TODO: Refactor this in something readable and idiomatic.
# This module might be redundant and this is the reason i wrote it the way it
# just works and doesn't look any good.


class FakeReport:
    """Class that helps generate fake data for functional TestCase"""

    programs = ['program' + str(i) for i in range(1, 6) for _ in range(2)]
    statuses = ['STARTED', 'STOPPED']

    def __init__(self, reverse=False):
        self.reverse = reverse

        if self.reverse:
            self.time_steps = [timedelta(minutes=5), timedelta(hours=1)]
            # attribute that should be used in test assertions
            self.work_time = {x: y for x, y in zip(
                self.programs[::2],
                [timedelta(minutes=240),
                 timedelta(minutes=300),
                 timedelta(minutes=300),
                 timedelta(minutes=245),
                 timedelta(minutes=240)]
            )}
            self.work_time['idle'] = timedelta(minutes=115)
        else:
            self.time_steps = [timedelta(hours=1), timedelta(minutes=5)]
            # attribute that should be used in test assertions
            self.work_time = {x: y for x, y in zip(
                self.programs[::2],
                [timedelta(minutes=300),
                 timedelta(minutes=300),
                 timedelta(minutes=250),
                 timedelta(minutes=240),
                 timedelta(minutes=240)]
            )}
            self.work_time['idle'] = timedelta(minutes=110)

        self.data = self.create_data()
        self.element_tree = self.build_etree()
        self.as_string = self.to_string()
        self.as_string_io = self.to_string_io()

    def to_string(self):
        """Writes generated HTML to string"""
        return tostring(self.element_tree,
                        pretty_print=True,
                        encoding='unicode')

    def to_string_io(self):
        """Writes generated HTML to file-like object StringIO"""
        return StringIO(self.as_string)

    def create_time_cols(self):
        """Generates time column data
        Particularly used as shortest sequence in
        zip(seq, cycle(), cycle()) statements in
        create_data() method to actually stop the infinite cycles and also
        generate time data to report.
        """
        time_col = [timedelta()] * 2 if self.reverse else [timedelta()]
        break_point = timedelta(days=1)
        time_data = timedelta()
        for time in cycle(self.time_steps):
            time_data += time
            # to make sure we don't generate data that goes beyond 1 day mark
            if time_data > break_point:
                break
            time_col.append(time_data)
        return time_col

    def create_data(self):
        """
        Method that created data list of lists that will be used for
        report generating
        """
        data = []
        dummy = 'DUMMY'
        for time, prg, status in zip(self.create_time_cols(),
                                     cycle(self.programs),
                                     cycle(self.statuses)
                                     ):
            data.append([time, prg, status, dummy, dummy])
        return data[1:] if self.reverse else data

    def build_td(self, lst):
        """Helper method to generate E.td() elements for build_etree()"""
        for item in lst:
            if not isinstance(item, str):
                # We must convert all non str types to str, otherwise builder
                # will raise exception.
                # use it to convert timedelta obj to str explicitly.
                try:
                    item = str(item)
                except ValueError as e:
                    raise e
            yield E.td(item)

    def build_etree(self):
        """Generates HTML code for a FakeReport"""
        body = (E.tr(*(i for i in self.build_td(y)))
                for _, y in enumerate(self.data))
        page = E.table(
            E.tr(
                E.th('TIME'),
                E.th('PROGRAM'),
                E.th('STATUS'),
                E.th('CYCLE TIME'),
                E.th('BEAM TIME'),
            ),
            *body
        )
        return page


if __name__ == '__main__':
    report1 = FakeReport()
    report2 = FakeReport(reverse=True)
    with open('report.html', 'w') as f1,\
            open('report_reverse.html', 'w') as f2:
        f1.write(report1.as_string)
        f2.write(report2.as_string)
