#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : yuyaban
# Created Date: 2023/10/24
# ---------------------------------------------------------------------------
import http.server
import socketserver
import json
import tweepy
from mastodon import Mastodon
import requests
from urllib.parse import parse_qs
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout
import os
import re
import sys
import mimetypes

# port number
PORT = 8080

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
BEARER_TOKERN = os.environ['BEARER_TOKERN']

MASTDN_CLIENT_KEY = os.environ['MASTDN_CLIENT_KEY']
MASTDN_CLIENT_SECRET = os.environ['MASTDN_CLIENT_SECRET']
MASTDN_ACCESS_TOKEN = os.environ['MASTDN_ACCESS_TOKEN']

FORSQUARE_ACCESS_TOKEN= os.environ['FORSQUARE_ACCESS_TOKEN']
FOURSQUARE_API_VERSION="20231024"

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def create_tw_client(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

        api = tweepy.API(auth)

        client = tweepy.Client(
            bearer_token=BEARER_TOKERN,
            consumer_key=CONSUMER_KEY, 
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN, 
            access_token_secret=ACCESS_SECRET
        )

        return client, api


    def create_mstdn_client(self):
        client = Mastodon(
            api_base_url  = 'https://mstdn.jp',
            client_id     = MASTDN_CLIENT_KEY,
            client_secret = MASTDN_CLIENT_SECRET,
            access_token  = MASTDN_ACCESS_TOKEN
        )

        return client


    def get_photo(self, photo):
        url = photo['prefix'] + "original" + photo['suffix']
        photo_path = "./data/tmp" + photo['suffix']

        res = requests.get(url)
        with open(photo_path, 'wb') as f:
            f.write(res.content)
        
        return photo_path


    def get_request(self, url, params):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except ConnectionError as ce:
            print("Connection Error:", ce)
            sys.exit(1)
        except HTTPError as he:
            print("HTTP Error:", he)
            sys.exit(1)
        except Timeout as te:
            print("Timeout Error:", te)
            sys.exit(1)
        except RequestException as re:
            print("Error:", re)
            sys.exit(1)
    

    def main(self, data):
        # main process
        print(f"[+] DEBUG: data['checkin']= {data['checkin']}")
        if 'checkin' in data:
            checkin_json = json.loads(data['checkin'])
            checkin_id = checkin_json['id']

            # get checkin details
            url = "https://api.foursquare.com/v2/users/self/checkins"
            checkin_params = {
                'oauth_token': FORSQUARE_ACCESS_TOKEN,
                'v': FOURSQUARE_API_VERSION,
                'limit': 1 # Number of latest checkins.
            }
            checkin = self.get_request(url, params=checkin_params)['response']['checkin']['items'][0]

            # Check if it matches the ID received by webhook
            if checkin['id'] != checkin_id:
                print("[+] ERROR: recieve checkin_id is missing.")
                return 0

            hasPhoto = False
            hasShout = False
            photo_path = ""
            post_msg = ""

            print(f"[+] DEBUG: checkin= {checkin}")
            # Check Photo
            if checkin['photos']['count'] > 0:
                hasPhoto = True
                photo_path = self.get_photo(checkin['photos']['items'][0])
            
            # Check message
            if 'shout' in checkin:
                hasShout = True

            # Note: Sometimes the trailing element of formattedAddress is a zip code and sometimes it is not.
            post_address = ""
            if not re.match(r'\d{3}-?\d{4}', checkin['venue']['location']['formattedAddress'][-1]):
                post_address = checkin['venue']['location']['formattedAddress'][-1] 
            else:
                post_address = checkin['venue']['location']['formattedAddress'][-2]

            checkinShortUrl = checkin['checkinShortUrl']

            if hasShout:
                post_msg = f"{checkin['shout']} (@ {checkin['venue']['name']} in {post_address}) {checkinShortUrl}"
            else:
                post_msg = f"I'm at {checkin['venue']['name']} in {post_address} {checkinShortUrl}"

            tw_client_v2, tw_api_v1 = self.create_tw_client()
            mstdn_client = self.create_mstdn_client()
            if hasPhoto:
                print("[+] INFO: hasPhoto")
                media = tw_api_v1.media_upload(filename=photo_path)
                tw_client_v2.create_tweet(text=post_msg, media_ids=[media.media_id])
                media_files = [mstdn_client.media_post(photo_path, mimetypes.guess_type(photo_path)[0])]
                mstdn_client.status_post(status=post_msg, media_ids=media_files, visibility="private")
                os.remove(photo_path)
            else:
                print("[+] INFO: NOT hasPhoto")
                tw_client_v2.create_tweet(text=post_msg)
                mstdn_client.status_post(status=post_msg, visibility="private")
            
            print(f"[+]INFO: posted: {post_msg}")
        else:
            print("[+] INFO: recv data is invalid.")

        return 0


    def do_POST(self):
        if "/webhook" == self.path:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
        
            # Format of recieved data is application/x-www-form-urlencoded.
            post_data = post_data.decode('utf-8')
            post_data = parse_qs(post_data)
            # excahnge to jason
            data = {key: value[0] for key, value in post_data.items()}

            # main process
            self.main(data)

            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404)
        
        return 0
    
    def do_GET(self):
        if "/healthcheck" == self.path:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("Healthy".encode())
        else:
            self.send_error(404)
        
        return 0

with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
