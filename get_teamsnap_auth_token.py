#!/usr/bin/env python3

"""
get_teamsnap_auth_token.py - Authorize user to use Teamsnap API.  Returns an access token.

By: Shaun Adkins - (github: adkinsrs)
"""

import argparse, json, requests, sys
import configparser

from oauthlib.oauth2 import WebApplicationClient, Client

# Teamsnap API authoization info -> https://www.teamsnap.com/documentation/apiv3/authorization
# Tutorial on OAuth2 -> https://testdriven.io/blog/oauth-python/

# OAuth2 WebApplicationClient forces the use of the "code" response type, so we have to use 3-leg OAuth flow.
# TODO: How to do with "token" response type, so we cna use 2-leg OAuth flow

def main():
	parser = argparse.ArgumentParser(description='Perform sync between Teamsnap and Meetup')
	parser.add_argument('-c', '--config', help='Path to config file', default='./config.ini')
	args = parser.parse_args()

	config = configparser.ConfigParser()
	config.read(args.config)

	# OAuth2 client setup
	client = WebApplicationClient(config['teamsnap']['client_id'])

	# This gets the authorization code (which expires after 10 mins)
	ts_auth_url = "https://auth.teamsnap.com/oauth/authorize"
	url = client.prepare_request_uri(
		ts_auth_url
	  , redirect_uri=config['teamsnap']['callback_url']
	  , scope="read"
	)

	print("\nAuthorization URL -> " + url + "\n")

 	# TODO: How to do without user intervention here
	auth_code = input("Go to the URL in the terminal, authorize, and enter the authorization code: ")

	# This allows us to exchange the auto_code for an access token
	data = client.prepare_request_body(
		code = auth_code
		, redirect_uri=config['teamsnap']['callback_url']
		, client_id = config['teamsnap']['client_id']
		, client_secret = config['teamsnap']['client_secret']
	)

	ts_token_url = 'https://auth.teamsnap.com/oauth/token'
	response = requests.post(ts_token_url, data=data)
	access_token = response.json()['access_token']
	print("\nSuccess!  Please add the following to the ACCESS_TOKEN setting in your config file: {}\n".format(access_token))

if __name__ == "__main__":
	main()
	sys.exit(0)
