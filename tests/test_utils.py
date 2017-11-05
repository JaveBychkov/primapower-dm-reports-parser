import unittest
from unittest.mock import Mock, patch
from datetime import timedelta, datetime
from collections import defaultdict

from cncparser.utils import (_convert_date, convert_timedelta,
                             filter_by_date, get_by_date,
                             _update_default_dict, aggregate_data,
                             simplify_job_name, sort_descending)


class TestGeneralPurposeUtilityFunctions(unittest.TestCase):

    def test_convert_timedelta_converting_dates_correctly(self):
        time = timedelta(seconds=3600)
        converted = convert_timedelta(time)
        self.assertEqual(converted, '1h 0m 0s')
        with self.assertRaises(TypeError):
            convert_timedelta(3600)

    def test_update_default_dict_method_works_as_expected(self):
        main = defaultdict(int, [('a', 1), ('b', 1), ('c', 1)])
        other = defaultdict(int, [('a', 4), ('d', 1)])
        _update_default_dict(main, other)
        self.assertEqual(dict(main), {'a': 5, 'b': 1, 'c': 1, 'd': 1})

    def test_convert_date_function_returns_timedelta_object(self):
        date_string = '1995-07-04'
        converted = _convert_date(date_string)
        self.assertEqual(converted, datetime(year=1995, month=7, day=4))
        date_string = '1995_07_04'
        converted = _convert_date(date_string, s_format='%Y_%m_%d')
        self.assertEqual(converted, datetime(year=1995, month=7, day=4))
        date_string = datetime(year=1995, month=7, day=4)
        converted = _convert_date(date_string)
        self.assertEqual(converted, datetime(year=1995, month=7, day=4))
        with self.assertRaises(TypeError):
            _convert_date(12345)

    def test_simplify_job_name_strips_path_and_version_tag(self):
        job_name = 'Metalware/Prefabricated/Housings/745.234.100ver20.05.ISO'
        simplified_name = simplify_job_name(job_name)
        self.assertEqual(simplified_name, '745.234.100.ISO')

    def test_sort_descending_returns_list_of_tuples_in_descending_order(self):
        d = {'prg1': 8, 'prg2': 1, 'prg3': 12, 'prg4': 4}
        sorted_tuples = sort_descending(d)
        self.assertEqual(sorted_tuples, [('prg3', 12), ('prg1', 8),
                                         ('prg4', 4), ('prg2', 1)]
                         )


class TestUtilityFunctionsThatWorksWithReportObjects(unittest.TestCase):

    def setUp(self):
        # Creating list of Mock objects with date attribute
        self.reports = [Mock() for x in range(5)]
        dates = (datetime(2017, 7, x) for x in range(1, 6))

        for x, y in zip(self.reports, dates):
            setattr(x, 'date', y)

    def test_filter_by_date_returns_desired_reports(self):
        max_date = datetime(2017, 7, 5)
        min_date = datetime(2017, 7, 3)
        filtered = filter_by_date(self.reports, min_date, max_date)
        # We should get reports with dates: 2017-07-03, 2017-07-04, 2017-07-05.
        self.assertCountEqual([x.date for x in filtered],
                              [datetime(2017, 7, x) for x in range(3, 6)])

    def test_get_by_date_returns_report_with_desired_date(self):
        desired_date = '2017-07-04'
        report = get_by_date(self.reports, desired_date)
        self.assertEqual(report.date, datetime(2017, 7, 4))
        desired_date = '2017-07-08'
        report = get_by_date(self.reports, desired_date)
        self.assertEqual(None, report)

    def test_aggregate_data_function_calls_update_function(self):
        with patch('cncparser.utils._update_default_dict') as mock:
            aggregate_data(self.reports)
            self.assertEqual(mock.call_count, 5)


if __name__ == '__main__':
    unittest.main()
