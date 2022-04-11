from icalendar import Calendar, Event
from datetime import datetime, timedelta
import requests
import boto3
import pytz


def get_matches_data(from_date, to_date):
    url = f"in_secret_note"
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


def put_to_bucket():
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("speedway-calendar")
    calendar = cal.to_ical()
    calendar_filename = "pge_ekstraliga.ics"
    bucket.put_object(Key=calendar_filename, Body=calendar, ACL="public-read")


cal = Calendar()

from_date = "2022-04-01"
to_date = "2022-10-17"
timezone = pytz.timezone("Europe/Warsaw")


def lambda_handler(event, context):
    data = get_matches_data(from_date, to_date)
    build_calendar_with_matches(data, cal)
    put_to_bucket()
