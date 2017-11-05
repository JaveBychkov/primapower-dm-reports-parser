from datetime import datetime, timedelta
from collections import defaultdict


def convert_timedelta(item):
    """Returns formated timedelta string representation

    Function used to covnert timedelta string representation form this:
    '1 day, 10:11:12' to this: '34h 11m 12s'.

    Parameters:
    -----------
    item : timedelta
        timedelta object that should be converted

    Returns:
    --------
    str
        timedelta string representation
    """
    if isinstance(item, timedelta):
        seconds = int(item.total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formated = '{}h {}m {}s'.format(hours, minutes, seconds)
    else:
        raise TypeError(item, 'is not timedelta object')
    return formated


def _convert_date(date_string, s_format='%Y-%m-%d'):
    """Returns datetime object

    Function used to convert string to datetime object.
    If date_string is already a datetime object just returns it.

    Parameters
    ----------
    date_string : string | datetime
        string or datetime object
    s_format : string
        format of the date_string

    Returns
    -------
    datetime
        datetime object converted or not converted from date_string
    """
    if isinstance(date_string, str):
        return datetime.strptime(date_string, s_format)
    elif isinstance(date_string, datetime):
        return date_string
    else:
        raise TypeError(date_string, 'is not a string or datetime object')


def filter_by_date(sequence, _min, _max):
    """Returns Report objects in _max, _min date range

    Parameters
    ----------
    data: sequence
        Sequence with Report objects to filter
    _max : str or datetime
        maximal date limit to filter
    _min : str or datetime
        minimal date limit to filter

    Returns
    -------
    set
        Set with report objects in _max, _min date range
        Empty if there is no reports in given range in sequence
    """
    _max, _min = [_convert_date(x) for x in (_max, _min)]
    return {x for x in sequence if _max >= x.date >= _min}


def get_by_date(sequence, date):
    """Returns report object from storage content according to passed date

    Parameters
    ----------
    date : str | datetime
        Interesting report's date.

    Returns
    -------
    Report
        Report object with .date == date
    None
        If there is no Report objects with .date == date in sequence

    Examples
    --------
    >>> get_by_date('2017_04_04')
    Report(2017_04_04.html, 2017_04_04)
    >>> get_by_date('2032_04_07')
    None
    """
    item = filter_by_date(sequence, date, date)
    return item.pop() if item else None


def _update_default_dict(main, other):
    """Summarize values of two defaultdicts

    Function sumarize two defaultdicts values if they both have similar
    keys and just adds key and value if don't

    Parameters
    ----------
    main : defaultdict
        dict that should be updated
    other : defaultdict
        dict which keys and values will be used to update main defaultdict

    Returns
    -------
    None
    """
    for k, v in other.items():
        main[k] += v


def aggregate_data(sequence):
    """Returns summarized data of all reports in passed sequence

    Parameters
    ----------
    to_dump : sequence
        Sequence that contains reports

    Returns
    -------
    defaultdict
        defauldict with summarized data of all passed reports
    """
    data = defaultdict(timedelta)
    for item in sequence:
        _update_default_dict(data, item)
    return data


def simplify_job_name(name):
    """Simplify job's path deleting it version tag and folder placement

    Parameters
    ----------
    name : str
        Program name
    Returns
    -------
    str
        simplified name

     Example
    -------
    >>> simplify_job_name('1/2/3/4/some_NAMEver23.04.ISO')
    some_NAME.ISO
    """
    name = name.split('/')[-1]
    if 'ver' in name:
        name = name.split('ver')[0] + '.ISO'
    return name


def sort_descending(dictionary):
    """Sort dictionary by value in descending order

    Parameters
    ----------
    dictionary : dict
        Dictionary to sort

    Returns
    -------
    list
        List of tuples that contain pairs of k, v

    Example
    -------
    >>> sort_descending({'a': 3, 'b': 2, 'c': 1})
    [('a', 3), ('b', 2), ('c', 1)]
    """
    return sorted(dictionary.items(), key=lambda x: x[1], reverse=True)
