from datetime import datetime, timedelta, date


def create_date_tuple(start_date, end_date):
    """
    Takes an input YYYY-MM-DD string and appends either 00:00:00 for start
     and  23:59:59  for end
    :param start_date: string like 2018-01-01
    :param end_date: string like 2018-01-01
    :return: datetime tuple for start and end
    """
    sd = datetime.strptime("{0} {1}".format(start_date, "00:00:00"), "%Y-%m-%d %H:%M:%S")
    ed = datetime.strptime("{0} {1}".format(end_date, "23:59:59"), "%Y-%m-%d %H:%M:%S")
    return sd, ed


def format_date_as_ymd(ts):
    """
    makes a datetime object pretty like 2019-10-31 10:23:45
    :param ts: a datetime object
    :return:
    """
    return ts.strftime("%Y-%m-%d")


def format_date_as_ymdhms(ts):
    """
    makes a datetime object pretty like 2019-10-31 10:23:45
    :param ts: a datetime object
    :return:
    """
    return ts.strftime("%Y-%m-%d %H:%M:%S")
