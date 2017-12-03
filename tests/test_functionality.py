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
            report.generate_report()
            f.write(report.html)
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
            fake_report = self.reports[report.name]

            self.assertEqual(report.idle_time, fake_report.timings['idle'])

            self.assertEqual(report.jobs, fake_report.jobs)

            self.assertEqual(report.busy_time, sum(fake_report.jobs.values(),
                                                   timedelta()))

            self.assertEqual(report.summary, fake_report.timings)


if __name__ == '__main__':
    unittest.main()
