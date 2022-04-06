from icalendar import Calendar, Event
from datetime import datetime, timedelta
import requests
import json
import pytz
import api_key

# TODO: change file path to incorporate __file__


def read_data_from_local_file():
    with open(r"./zuzel_data.json", "r") as f:
        data = json.load(f)
    return data


def get_matches_data(from_date, to_date):
    url = api_key.pge_api_key(from_date, to_date)
    response = requests.get(url)
    return response.json()


def extract_match_details(match):
    shortname = match["shortname"]["pl"]
    datetime_schedule = match["datetime_schedule"]
    starting_time = datetime.fromtimestamp(datetime_schedule / 1000, timezone)
    if match["broadcaster_schedule"] is not None:
        broadcaster = match["broadcaster_schedule"]["title"]
    else:
        broadcaster = ""
    return shortname, starting_time, broadcaster


def create_cal_event(shortname, starting_time, broadcaster):
    cal_event = Event()
    cal_event.add("summary", shortname)
    cal_event.add("dtstart", starting_time)
    cal_event.add("duration", timedelta(hours=2, minutes=15))
    cal_event.add("location", broadcaster)
    return cal_event


def build_calendar_with_matches(data, cal):
    for match in data["data"]:
        shortname, starting_time, broadcaster = extract_match_details(match)
        print(shortname, starting_time, broadcaster)
        cal_event = create_cal_event(shortname, starting_time, broadcaster)
        cal.add_component(cal_event)


def save_cal_to_file(cal):
    calendar = cal.to_ical()
    calendar_filename = "pge_ekstraliga.ics"
    with open(calendar_filename, "wb") as f:
        f.write(calendar)


cal = Calendar()

from_date = "2022-04-01"
to_date = "2022-10-17"
timezone = pytz.timezone("Europe/Warsaw")

data = read_data_from_local_file()
# data = get_matches_data(from_date, to_date)
build_calendar_with_matches(data, cal)
# save_cal_to_file(cal)
