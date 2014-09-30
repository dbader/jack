#!/usr/bin/env python
import datetime
import glob
import gzip
import os
import sys

import dateutil.parser
import pytz

TZINFOS = {
    'UTC': pytz.utc,
    'HST': pytz.timezone('US/Hawaii'),
    'AKDT': pytz.timezone('US/Alaska'),
    'PDT': pytz.timezone('US/Pacific'),
    'MDT': pytz.timezone('US/Mountain'),
    'CDT': pytz.timezone('US/Central'),
    'EDT': pytz.timezone('US/Eastern'),
    'CET': pytz.timezone('Europe/Berlin'),
}


def parse_timestamp(ts):
    # This could re-parse on error with fuzzy=True
    # and just log a message that says
    # "Invalid input but I'm parsing this as xyz"
    dt = dateutil.parser.parse(ts, fuzzy=True, tzinfos=TZINFOS)
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=dateutil.tz.tzlocal())
    return dt


def test_parse_timestamp():
    assert parse_timestamp('2014-01-01')
    assert parse_timestamp('8:22')
    assert parse_timestamp('8:22pm')
    assert parse_timestamp('2014-01-01 8:22pm')
    assert parse_timestamp('2014-01-01 8:22pm PDT')
    assert parse_timestamp('2014-01-01 8:22pm UTC')
    assert parse_timestamp('14:33 UTC')
    assert parse_timestamp('8:33am PDT') != parse_timestamp('8:33am CEST')
    assert parse_timestamp('Jul 13 06:42:56')  # scribe syslog


def normalize_to_utc(dt):
    return dt.astimezone(pytz.utc)


def test_normalize_to_utc():
    pdt_ts = parse_timestamp('2014-01-01 10:00 PDT')
    assert normalize_to_utc(pdt_ts).hour == 17
    utc_ts = parse_timestamp('2014-01-01 10:00')
    assert normalize_to_utc(utc_ts).hour == 18
    utc_ts = parse_timestamp('2014-01-01 10:00 UTC')
    assert normalize_to_utc(utc_ts).hour == 10


def parse_args(args):
    args = args[1:]
    return [_.strip() for _ in ' '.join(args).split('to')]


def test_parse_args():
    args = parse_args(['jack', '8:22pm', 'to', '8:30pm'])
    assert args[0] == '8:22pm'
    assert args[1] == '8:30pm'
    args = parse_args(['jack', '8:22pm', 'to', '8:30pm PDT'])
    assert args[0] == '8:22pm'
    assert args[1] == '8:30pm PDT'


def last_modified_date(filename):
    """Last modified timestamp as a UTC datetime"""
    mtime = os.path.getmtime(filename)
    dt = datetime.datetime.utcfromtimestamp(mtime)
    return dt.replace(tzinfo=pytz.utc)


def all_logs():
    return glob.glob('*log*')


DATE_FORMAT = 'Jul 20 06:39:45'  # So we can grab the length
def parse_log_timestamp(line):
    raw_timestamp = line[0:len(DATE_FORMAT)]
    timestamp = parse_timestamp(raw_timestamp)
    # Assume log timestamps are in UTC
    return timestamp.replace(tzinfo=pytz.utc)


def open_log(filename):
    if filename.endswith('.gz'):
        return gzip.GzipFile(filename)
    else:
        return open(filename)


def main(argv):
    args = parse_args(argv)
    query_start = parse_timestamp(args[0])
    query_end = parse_timestamp(args[1])

    # Force both timestamps to be in the same timezone
    query_start = query_start.replace(tzinfo=query_end.tzinfo)

    print query_start
    print query_end

    query_start = normalize_to_utc(query_start)
    query_end = normalize_to_utc(query_end)

    print query_start
    print query_end

    # Sort on last modified, earliest to latest
    logs = sorted([
        (last_modified_date(filename), filename)
        for filename in all_logs()
    ])

    print logs

    logs_to_search = []
    prev_log_end = query_start - datetime.timedelta(days=1000 * 365)
    for log_end, log_filename in logs:
        if query_start <= log_end and query_start >= prev_log_end:
            logs_to_search.append(log_filename)
        prev_log_end = log_end

    print logs_to_search

    for filename in logs_to_search:
        logfile = open_log(filename)
        for line in logfile:
            log_ts = parse_log_timestamp(line)
            if log_ts >= query_start and log_ts <= query_end:
                sys.stdout.write(line)
            if log_ts > query_end:
                break
        logfile.close()


def _main():
    sys.exit(main(sys.argv))


if __name__ == '__main__':
    _main()
