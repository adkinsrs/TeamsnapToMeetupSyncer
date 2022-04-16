#!/usr/bin/env python3

"""
teamsnap_to_meetup_syncer.py - Sync attended events on Teamsnap to also be attended on Meetup

By: Shaun Adkins - (github: adkinsrs)
"""

import argparse, json, requests, sys
import configparser
import logging

from collections import namedtuple
from datetime import datetime

# NOTE: NOW is initially not timezone aware (naive), so need to add timezone offset to NOW
NOW = datetime.now(datetime.timezone.utc).astimezone()

TEAMSNAP_API_HREF="https://api.teamsnap.com/v3"

TimeRange = namedtuple("TimeRange", "start end")

"""
Steps: (have cron to run daily)

1. [Teamsnap] Retrieve list of all events from team
2. [Teamsnap] Parse out date and time of "attending" ones for ones after today's date
3. [Meetup] Retrieve list of upcoming events from organization
4. [Meetup] For events that have no "attending" status, if time/date line up with something attending on Teamsnap, then mark as "attending".
"""

def get_ts_url_response_json(uri, header, params={}):
    """Perform GET request on url and return JSON."""

    # If params are provided, then add "search" rel force query on params
    uri += "/search" if params else ""
    response = requests.get(uri, headers=header, params=params)
    if response.status_code != 200:
        raise Exception("Error: {}".format(response.status_code))
    return response.json()

def retrieve_attending_ts_event_hrefs(avail_items, sync_maybe=False):

    # Possible status codes for availability:
    # No - 0
    # Yes - 1
    # Maybe - 2
    # Unknown - None
    attending_event_hrefs = []
    for item in avail_items:
        data = item["data"]
        event_href = next(filter(lambda x: x["rel"] == "event", item["links"]))["href"]
        status_code = next(filter(lambda x: x["name"] == "status_code", data))
        if status_code["value"] == 1:
            attending_event_hrefs.append(event_href)
        if sync_maybe and status_code["value"] == 2:
            attending_event_hrefs.append(event_href)

    return attending_event_hrefs

def retrieve_future_ts_event_time_ranges(attending_ts_event_hrefs, header):
    """Retrieve time ranges for future events that member is attending."""

    time_ranges = []
    for event in attending_ts_event_hrefs:
        ts_event_json = get_ts_url_response_json(event, header)
        ts_event_data = ts_event_json["collection"]["items"][0]['data']
        # Times are stored as UTC, so add timezone offset.
        ts_arrival_date = next(filter(lambda x: x["name"] == "arrival_date", ts_event_data))["value"]
        ts_end_date = next(filter(lambda x: x["name"] == "end_date", ts_event_data))["value"]
        ts_tz_offset = next(filter(lambda x: x["name"] == "time_zone_offset", ts_event_data))["value"]

        # Add time zone offset to date strings
        try:
            if ts_arrival_date.endswith("Z"):
                ts_arrival_date = ts_arrival_date[:-1]
            ts_arrival_date += ts_tz_offset
            ts_iso_arrival_date = datetime.fromisoformat(ts_arrival_date)

            if ts_end_date.endswith("Z"):
                ts_end_date = ts_end_date[:-1]
            ts_end_date += ts_tz_offset
            ts_iso_end_date = datetime.fromisoformat(ts_end_date)
        except AttributeError:
            # Ran into some edge cases where the string was None, so just skip it.
            continue

        # If the event is in the future, then add it to the list of time ranges

        if ts_iso_end_date < NOW:
            continue
        time_ranges.append(TimeRange(ts_iso_arrival_date, ts_iso_end_date))
    return time_ranges

def main():
    parser = argparse.ArgumentParser(description='Perform sync between Teamsnap and Meetup')
    parser.add_argument('-c', '--config', help='Path to config file', default='./config.ini')
    parser.add_argument('--sync_maybe', help='Sync "Maybe" events in addition to ones marked "Yes" for attending ', action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    config = configparser.ConfigParser()
    config.read(args.config)

    ### TEAMSNAP ###

    ts_access_token = config['teamsnap']['access_token']
    ts_user_id = config['teamsnap']['user_id']
    ts_team_id = config['teamsnap']['team_id']

    header = {
        'Authorization': 'Bearer {}'.format(ts_access_token)
    }

    ts_root_json = get_ts_url_response_json(TEAMSNAP_API_HREF, header)

    # These are a collection of URLs that are stored within the API. Will still work if the URL is changed.
    ts_links = ts_root_json["collection"]["links"]
    ts_availability_href = next(filter(lambda x: x["rel"] == "availabilities", ts_links))["href"]
    ts_members_href = next(filter(lambda x: x["rel"] == "members", ts_links))["href"]

    # Get member ID of user for this team
    params =  {"team_id": ts_team_id, "user_id": ts_user_id}
    ts_member_json = get_ts_url_response_json(ts_members_href, header, params)

    # Get member id.  Should only appear once
    ts_member_data = ts_member_json["collection"]["items"][0]['data']
    ts_member_id = next(filter(lambda x: x["name"] == "id", ts_member_data))["value"]

    # Get list of availabilities for this member
    params = {"team_id": ts_team_id, "member_id": ts_member_id}
    ts_availability_json = get_ts_url_response_json(ts_availability_href, header, params)
    ts_avail_items = ts_availability_json["collection"]["items"]

    # Filter for availabilities that member is attending.  Grab the event hrefs
    attending_ts_event_hrefs = retrieve_attending_ts_event_hrefs(ts_avail_items, args.sync_maybe)

    # Get time ranges for future events that member is attending
    future_time_ranges = retrieve_future_ts_event_time_ranges(attending_ts_event_hrefs, header)

    ### MEETUP ###


if __name__ == "__main__":
    main()
    sys.exit(0)
