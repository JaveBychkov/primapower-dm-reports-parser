import unittest
from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch, call

from cncparser.report import (Report, convert_time, parse, read_folder,
                              read_report)

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

    @patch('cncparser.report.os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    def test_read_report_creates_instances_of_report(self, f_mock, ex_mock):
        path = 'C:/CNC/jobs/reports/2017_07_04.html'
        with patch('cncparser.report.Report') as report_mock:
            report = read_report(path)
            self.assertEqual(report, report_mock.return_value)
            report_mock.assert_called_with(path)
            f_mock.assert_called_once_with(path)
            ex_mock.assert_called_once_with(path)

    def test_read_report_raises_error_if_file_not_found(self):
        path = 'C:/CNC/jobs/reports/2017_07_04.html'
        msg = 'Please, make sure that {} file exists'.format(path)
        with self.assertRaises(FileNotFoundError, msg=msg):
            read_report(path)

    @patch('cncparser.report.os.path.isdir', return_value=True)
    @patch('cncparser.report._read_folder', return_value=True)
    def test_read_folder_calls_real_function(self, real_f_mock, isdir_m):
        path = 'C:/CNC/jobs/reports'
        read_folder(path)
        real_f_mock.assert_called_once_with(path)

    @patch('cncparser.report.os.path.isdir', return_value=True)
    @patch('cncparser.report.os.listdir',
           return_value=['file1.html', 'file2.html', 'somefile.iso'])
    def test_read_folder_returns_report_objects(self, listdir_m, isdir_m):
        path = 'C:/CNC/jobs/reports'
        with patch('cncparser.report.Report') as report_mock:
            list(read_folder(path))  # Consume generator.
            self.assertEqual(report_mock.call_count, 2)
            calls = [
                (call('C:/CNC/jobs/reports/file1.html')),
                (call('C:/CNC/jobs/reports/file2.html'))
            ]
            self.assertEqual(calls, report_mock.call_args_list)

    def test_read_folder_raises_not_a_directory_error(self):
        path = 'C:/CNC/jobs/reports'
        msg = '{} is not a folder'.format(path)
        with self.assertRaises(NotADirectoryError, msg=msg):
            read_folder(path)

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

    def test_date_from_path_returns_date_representation_of_a_string(self):
        self.assertEqual(self.report.date, date(2017, 7, 4))

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
