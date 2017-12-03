## Prima Power CNC Reports Parser
Little library that can extract data from CNC usage reports
### Getting Started
---
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
#### Installing
At first you might want to create a new virtual env, i'll leave it up to you.

To get started with the package you need to clone project and install it using `pip`:

```
$ git clone https://github.com/JaveBychkov/upgraded-chainsaw.git cncparser
$ cd cncparser
$ pip install .
```
This commands will install `lxml>=3.7` package and `cncparser` package. 

### Running the tests
---
To run tests you simply do:
```
$ python -m unittest discover
```
### Basic usage
---

Parsing single report:
```python
import cncparser

report = cncparser.read_report(report_path)
```
Now you can access various attributes:
```python
report.path  # Path to the report location.
report.name  # Report name.
report.date  # Python datetime reprsentation of date.
report.date_as_string  # String representation of date.
report.data  # Raw, unproccessed report data.
report.summary  # Proccesed, summarized data from the report.
report.idle_time  # Summary of the time laser was inactive.
report.busy_time  # Dictionary where keys are job's names and values are time jobs were in work.
```
Basic use case is to write collected data to **CSV** file, example below will write  idle times for all reports in current folder to an `idle_time_data.csv` file.
```python
import os
import csv

import cncparser

files = [f for f in os.listdir('.') if f.endswith('.html')]

reports = [cncparser.read_report(f) for f in files]

sorted_reports = sorted([(r.date, r.idle_time) for r in reports],
                        key=lambda x: x[1])

with open('idle_time_data.csv', 'w', newline='') as output:
    writer = csv.writer(output)
    writer.writerow(['Date', 'Time'])
    for data in sorted_reports:
        writer.writerow(data)
```






