import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from io import StringIO

from cncparser.report import Report, read_report, parse, convert_time


SAMPLE = StringIO("""
<TABLE>
    <TR>
        <TH>ShouldBeRippedOff</TH>
        <TH>ShouldBeRippedOff</TH>
        <TH>ShouldBeRippedOff</TH>
        <TH>ShouldBeRippedOff</TH>
    </TR>
    <TR>
        <TD>00:00:00</TD>
        <TD>sub/sub/sub/Pr1.ISO</TD>
        <TD>STARTED</TD>
        <TD>ShouldBeRippedOff</TD>
    </TR>
    <TR>
        <TD>01:00:00</TD>
        <TD>sub/sub/sub/Pr1.ISO</TD>
        <TD>STOPPED</TD>
        <TD>ShouldBeRippedOff</TD>
    </TR>
    <TR>
        <TD>01:05:00</TD>
        <TD>sub/sub/sub/Pr2.ISO</TD>
        <TD>STARTED</TD>
        <TD>ShouldBeRippedOff</TD>
    </TR>
    <TR>
        <TD>02:05:00</TD>
        <TD>sub/sub/sub/Pr2.ISO</TD>
        <TD>STOPPED</TD>
        <TD>ShouldBeRippedOff</TD>
    </TR>

</TABLE>""")

PARSED_DATA = [
    (timedelta(seconds=0), 'sub/sub/sub/Pr1.ISO', 'STARTED'),
    (timedelta(seconds=3600), 'sub/sub/sub/Pr1.ISO', 'STOPPED'),
    (timedelta(seconds=3900), 'sub/sub/sub/Pr2.ISO', 'STARTED'),
    (timedelta(seconds=7500), 'sub/sub/sub/Pr2.ISO', 'STOPPED')
]


SUMMARY = {'sub/sub/sub/Pr1.ISO': timedelta(seconds=3600),
           'sub/sub/sub/Pr2.ISO': timedelta(seconds=3600),
           'idle': timedelta(seconds=79200)}


class TestParsingRealtedFunctions(unittest.TestCase):

    def test_main_interface_returns_report_object(self):
        path = 'C:/CNC/jobs/reports/2017_07_04.html'
        with patch('cncparser.report.parse') as parse_mock, \
                patch('cncparser.report.Report.sum_data'):
            parse_mock.return_value = 'Something'
            report = read_report(path)
            self.assertIsInstance(report, Report)
            parse_mock.assert_called_with(path)
            self.assertEqual(report.name, '2017_07_04.html')
            self.assertEqual(report.date, datetime(2017, 7, 4))

    def test_convert_time_function_returns_timedelta_object_from_string(self):
        time_string = '10:11:12'
        converted_time = convert_time(time_string)
        self.assertIsInstance(converted_time, timedelta)
        self.assertEqual(converted_time.total_seconds(), 36672)

    def test_parse_function_yields_tuples_of_parsed_date(self):
        parsed = parse(SAMPLE)
        for pos, item in enumerate(parsed):
            self.assertEqual(PARSED_DATA[pos], item)
        self.assertFalse(list(parsed))


class TestReportObjectBehaving(unittest.TestCase):

    @patch('cncparser.report.parse', return_value=PARSED_DATA)
    def setUp(self, mock):
        self.report = Report('C:/CNC/jobs/reports/2017_07_04.html')

    def test_name_from_path_returns_expected_name(self):
        self.assertEqual(self.report.name, '2017_07_04.html')

    def test_date_from_path_returns_datetime_representation_of_string(self):
        self.assertEqual(self.report.date, datetime(2017, 7, 4))

    def test_date_as_string_property(self):
        self.assertEqual(self.report.date_as_string, '2017-07-04')

    def test_idle_time_property(self):
        self.assertEqual(self.report.idle_time, timedelta(seconds=79200))

    def test_busy_time_property(self):
        self.assertEqual(self.report.busy_time, timedelta(seconds=7200))

    def test_jobs_property(self):
        self.assertEqual(self.report.jobs,
                         {'sub/sub/sub/Pr1.ISO': timedelta(seconds=3600),
                          'sub/sub/sub/Pr2.ISO': timedelta(seconds=3600)}
                         )

    def test_sum_data_returns_summarized_data(self):
        self.assertEqual(dict(self.report.summary), SUMMARY)


if __name__ == '__main__':
    unittest.main()
