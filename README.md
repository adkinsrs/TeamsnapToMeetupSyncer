# TeamsnapToMeetupSyncer

I'm tired of having to fill out two different calendars for events.  Let's sync events i'm attending on teamsnap to meetup

## Steps to take if you are missing certain pieces of information in your config.ini file

### If you do not have ACCESS_TOKEN filled in your config.ini file

If you have CLIENT_ID, CLIENT_SECRET, and CALLBACK_URL populated in your config.ini you can skip step 1.

1. Login to https://auth.teamsnap.com/ and create an application.  You should fill out the fields (I use the local URI string for my redirect URI), and hit Submit. You should see a Client ID, Client Secret, and Callback URI, all which go into your config file.
2. In your terminal, `python3 get_teamsnap_access_token.py`. This will print a URL in your terminal where, after clicking it, you can authorize your logged in TeamSnap user to use this application you created.
3. The next page will have an authorization code.  Copy and paste that into the terminal, where it will now print out an access code, which should be added to the ACCESS_TOKEN section of your config

Once you have obtained an ACCESS_TOKEN you do not need to repeat these steps in the future. This access token is specific for this logged in user, so other users will need a different access token to provide.

### If you do not have USER_ID and/or TEAM_ID filled in your config.ini file

Please run `python3 teamsnap_find_user_and_team_id.py`.  The printed output will contain the logged in user's "user_id" and the first "team_id" found. You can place these in your config.ini file, and skip this step in the future

## Usage

```python

usage: teamsnap_to_meetup_syncer.py [-h] [-c CONFIG] [--sync_maybe] [-v] [-vv]

Perform sync between Teamsnap and Meetup

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config file
  --sync_maybe          Sync "Maybe" events in addition to ones marked "Yes" for attending
  -v, --verbose         Verbose output
  -vv, --very_verbose   Very verbose output

  ```