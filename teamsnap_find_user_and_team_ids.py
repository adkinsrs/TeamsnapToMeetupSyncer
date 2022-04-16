#!/usr/bin/env python3

"""
teamsnap_find_user_and_team_ids.py

Description:
Use the API to find the user and team IDs in teamsnap which can be put in the config file for future reference.
Assumes that the user has just one particular team, as the script is hardcoded to retrieve the first team.

By: Shaun Adkins - (github: adkinsrs)
"""

import argparse, json, requests, sys
import configparser

TEAMSNAP_API_HREF="https://api.teamsnap.com/v3"



def main():
	parser = argparse.ArgumentParser(description='Perform sync between Teamsnap and Meetup')
	parser.add_argument('-c', '--config', help='Path to config file', default='./config.ini')
	args = parser.parse_args()

	config = configparser.ConfigParser()
	config.read(args.config)

	ts_access_token = config['teamsnap']['access_token']

	header = {
		'Authorization': 'Bearer {}'.format(ts_access_token)
	}

	try:
		res = requests.get(
			TEAMSNAP_API_HREF
			, headers = header
		)
	except requests.exceptions.RequestException as e:
		print(e)
		sys.exit(1)

	res_json = res.json()

	# These are a collection of URLs that are stored within the API. Will still work if the URL is changed.
	ts_links = res_json["collection"]["links"]
	ts_me_href = next(filter(lambda x: x["rel"] == "me", ts_links))["href"]

	print("Retrieved Teamsnap links")

	try:
		res = requests.get(
			ts_me_href
			, headers = header
		)
	except:
		print("Error: Could not retrieve user information from Teamsnap")
		sys.exit(1)

	res_json = res.json()
	# Get user name.  Should only appear once
	ts_user_data = res_json["collection"]["items"][0]['data']
	ts_user_id = next(filter(lambda x: x["name"] == "id", ts_user_data))["value"]
	ts_user_links = res_json["collection"]["items"][0]["links"]
	ts_teams_href = next(filter(lambda x: x["rel"] == "teams", ts_user_links))["href"]

	print("Retrieved user ID: {}".format(ts_user_id))

	try:
		res = requests.get(
			ts_teams_href
			, headers = header
		)
	except:
		print("Error: {}".format(sys.exc_info()[0]))
		sys.exit(1)

	res_json = res.json()
	# Get team ID.  Should only appear once
	ts_team_data = res_json["collection"]["items"][0]['data']
	ts_team_id = next(filter(lambda x: x["name"] == "id", ts_team_data))["value"]

	print("Retrieved team ID: {}".format(ts_team_id))

if __name__ == "__main__":
	main()
	sys.exit(0)
