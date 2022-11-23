import random
import cProfile
import datetime
import dateutil.tz
import dateutil.parser

def generate_datetime(min_year=1900, max_year=datetime.datetime.now().year):
    start = datetime.datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + datetime.timedelta(days=365 * years)
    return (start + (end - start) * random.random()).replace(microsecond=0)

def convert_str_to_datetime_using_strptime(s: str) -> datetime:
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")

def convert_str_to_datetime_using_string_parsing(s: str) -> datetime:
    year = int(s[:4])
    month = int(s[5:7])
    day = int(s[8:10])
    hour = int(s[11:13])
    minute = int(s[14:16])
    second = int(s[17:19])
    timezone_offset_hours_int = int(s[19:22])
    timezone_delta = datetime.timedelta(hours=timezone_offset_hours_int)
    if timezone_offset_hours_int < 0:
        timezone_delta *= -1
    timezone_offset = dateutil.tz.tzoffset(None, timezone_delta)
    return datetime.datetime(year, month, day, hour, minute, second, tzinfo=timezone_offset)

def convert_str_to_datetime_using_dateutil_parser(s: str) -> datetime:
    return dateutil.parser.parse(s)

def run_using_strptime(datetime_strings):
    print(f"Используя strptime при обработке {len(datetime_strings)} строк")
    return [convert_str_to_datetime_using_strptime(s) for s in datetime_strings]

def run_using_string_parsing(datetime_strings):
    print(f"Используя парсинг строки при обработке {len(datetime_strings)} строк")
    return [convert_str_to_datetime_using_string_parsing(s) for s in datetime_strings]

def run_using_dateutil_parser(datetime_strings):
    print(f"Используя dateutil.parser при обработке {len(datetime_strings)} строк")
    return [convert_str_to_datetime_using_dateutil_parser(s) for s in datetime_strings]

random_datetimes_as_strings = [generate_datetime().isoformat() + "+0300" for i in range(100000)]
cProfile.run("run_using_strptime(random_datetimes_as_strings)")
cProfile.run("run_using_string_parsing(random_datetimes_as_strings)")
cProfile.run("run_using_dateutil_parser(random_datetimes_as_strings)")