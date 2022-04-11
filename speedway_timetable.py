from icalendar import Calendar, Event
from datetime import datetime, timedelta
import os
import requests
import json
import pytz
import api_key


def read_data_from_local_file():
    file_path = set_file_path("speedway_data.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def set_file_path(filename):
    script_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_path, filename)
    return file_path


def get_matches_data(from_date, to_date):
    url = api_key.pge_api_key(from_date, to_date)
    response = requests.get(url)
    return response.json()


def extract_match_details(match):
    datetime_schedule = match["datetime_schedule"]
    starting_time = datetime.fromtimestamp(datetime_schedule / 1000, timezone)
    if match["broadcaster_schedule"] is not None:
        broadcaster = match["broadcaster_schedule"]["title"]
        if "/" in broadcaster:
            broadcaster = broadcaster.split("/")[0].strip()
    else:
        broadcaster = ""
    if (
        match["card_teams"]
        and match["card_teams"][0]["match_score"] is not None
    ):
        team_a = match["card_teams"][0]
        team_a_result = f"{team_a['team_shortcut']} {team_a['match_score']}"
        team_b = match["card_teams"][1]
        team_b_result = f"{team_b['match_score']} {team_b['team_shortcut']}"
        shortname = f"{team_a_result} - {team_b_result}"
    else:
        shortname = match["shortname"]["pl"]
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
    file_path = set_file_path(calendar_filename)
    with open(file_path, "wb") as f:
        f.write(calendar)


def save_data_to_file(data):
    file_path = set_file_path("speedway_data.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


cal = Calendar()

from_date = "2022-04-01"
to_date = "2022-04-20"
timezone = pytz.timezone("Europe/Warsaw")

# data = read_data_from_local_file()
data = get_matches_data(from_date, to_date)
save_data_to_file(data)
build_calendar_with_matches(data, cal)
save_cal_to_file(cal)
