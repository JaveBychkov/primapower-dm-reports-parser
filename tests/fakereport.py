from collections import defaultdict
from datetime import timedelta
from itertools import cycle


RUNTIME = timedelta(hours=1)  # program run time.
PAUSE = timedelta(minutes=5)  # break after program execution ended.
DAYTIME = timedelta(days=1)


# Code Still needs refactoring but it's alot better than it was.


class FakeReport:

    def __init__(self, reverse=False):
        self.reverse = reverse
        self.programs = ('prg1', 'prg2', 'prg3', 'prg4', 'prg5')
        self.html = """
        <html>
            <table>
                <th>
                    <td>time</td>
                    <td>program</td>
                    <td>status</td>
                </th>
        """
        self.timings = defaultdict(timedelta)
        self.current_time = timedelta()

    @property
    def jobs(self):
        return {k: v for k, v in self.timings.items() if k != 'idle'}

    def start_program(self, program):
        self.html += """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>STARTED</td>
        </tr>
        """.format( self.current_time, program)

    def end_program(self, program):
        if not self.reverse:
            self.current_time += RUNTIME
            self.timings[program] += RUNTIME
        self.html += """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>STOPPED</td>
        </tr>
        """.format(self.current_time, program)
        self.current_time += PAUSE
        self.timings['idle'] += PAUSE

    def check_limits(self, program):
        if self.current_time + PAUSE >= DAYTIME:
            self.end_cycle('idle')
            return True
        elif self.current_time + RUNTIME >= DAYTIME:
            self.end_cycle(program)
            return True
        

    def end_cycle(self, status):
        if status in self.programs:
            self.start_program(status)
            self.timings[status] += DAYTIME - self.current_time
        else:
            self.timings[status] += DAYTIME - self.current_time
        self.html += '</table></html>'

    def generate_report(self):
        for program in cycle(self.programs):
            if not self.reverse:
                if self.check_limits(program):
                    break
                self.start_program(program)
                self.end_program(program)
            else:
                self.end_program(program)
                self.reverse = False
        assert sum(self.timings.values(), timedelta()) == timedelta(days=1)


if __name__ == '__main__':
    with open('r1.html', 'w') as f, open('r2.html', 'w') as f2:
        r1 = FakeReport()
        r1.generate_report()
        r2 = FakeReport(reverse=True)
        r2.generate_report()
        f.write(r1.html)
        f2.write(r2.html)