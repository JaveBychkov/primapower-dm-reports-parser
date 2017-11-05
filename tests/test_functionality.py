import os
import unittest
from datetime import timedelta
from tempfile import TemporaryDirectory

import cncparser
from tests.fakereport import FakeReport

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class SimpleFunctionalTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = TemporaryDirectory(dir=BASE_DIR)
        self.reports = {}
        for i in range(1, 4):
            name = '2017_04_0{}.html'.format(i)
            f = open(os.path.join(self.tmp_dir.name, name), 'w')
            if not i % 2:
                report = FakeReport(reverse=True)
            else:
                report = FakeReport()
            self.reports[name] = report
            f.write(report.as_string)
            f.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_can_parse_and_store_reports_data(self):
        # Main parsing proccess
        directory = os.path.join(BASE_DIR, self.tmp_dir.name)
        files = os.listdir(directory)
        parsed = []

        for report in files:
            path = os.path.join(directory, report)
            parsed.append(cncparser.read_report(path))

        # Assertions goes below

        self.assertEqual(len(parsed), 3)

        names = [x.name for x in parsed]

        self.assertCountEqual(names, self.reports.keys())

        for report in parsed:
            work_time = self.reports[report.name].work_time
            busy = [work_time[key] for key in work_time if key != 'idle']

            self.assertEqual(report.idle_time, work_time['idle'])

            jobs = {k: v for k, v in work_time.items() if k != 'idle'}
            self.assertEqual(report.jobs, jobs)

            self.assertEqual(report.busy_time, sum(busy, timedelta()))

            self.assertEqual(report.summary, work_time)


if __name__ == '__main__':
    unittest.main()
