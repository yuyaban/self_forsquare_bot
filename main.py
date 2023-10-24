#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : yuyaban
# Created Date: 2023/10/24
# ---------------------------------------------------------------------------

import tweepy
from mastodon import Mastodon
import requests
import time
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout
import datetime
import os
import re
import sys
import mimetypes

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
BEARER_TOKERN = os.environ['BEARER_TOKERN']

MASTDN_CLIENT_KEY = os.environ['MASTDN_CLIENT_KEY']
MASTDN_CLIENT_SECRET = os.environ['MASTDN_CLIENT_SECRET']
MASTDN_ACCESS_TOKEN = os.environ['MASTDN_ACCESS_TOKEN']

FORSQUARE_ACCESS_TOKEN= os.environ['FORSQUARE_ACCESS_TOKEN']

LAST_POST_MEMO_PATH = "./data/last_post"

def create_tw_client():
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

def create_mstdn_client():
    client = Mastodon(
        api_base_url  = 'https://mstdn.jp',
        client_id     = MASTDN_CLIENT_KEY,
        client_secret = MASTDN_CLIENT_SECRET,
        access_token  = MASTDN_ACCESS_TOKEN
    )

    return client

def get_request(url, params):
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

def get_photo(photo):
    url = photo['prefix'] + "original" + photo['suffix']
    photo_path = "./data/tmp" + photo['suffix']

    res = requests.get(url)
    with open(photo_path, 'wb') as f:
        f.write(res.content)
    
    return photo_path

def main():
    post_ids = []
    # check last post
    with open(LAST_POST_MEMO_PATH, 'r') as f:
        last_posts_ids = f.readlines()

    # checkins list
    now_dt = datetime.datetime.now()
    before_dt = now_dt - datetime.timedelta(minutes=2) 

    unitxtime_after = int(before_dt.timestamp())
    unixtime_before = int(now_dt.timestamp())
    url = f"https://api.foursquare.com/v2/users/self/checkins"
    #url = f"https://api.foursquare.com/v2/users/self/checkins?v=20231022&oauth_token={FORSQUARE_ACCESS_TOKEN}&limit=2"
    checkin_params = {
        'oauth_token': FORSQUARE_ACCESS_TOKEN,
        'v': '20231024',  # Foursquare APIのバージョンを指定
        'afterTimestamp': unitxtime_after,  # 開始時刻のタイムスタンプ
        'beforeTimestamp': unixtime_before  # 終了時刻のタイムスタンプ
    }

    checkins_json = get_request(url, checkin_params)

    for d in checkins_json['response']['checkins']['items']:
        if d['id']+"\n" in last_posts_ids:
            print(f"[+] INFO: Already Posted.")
            continue

        hasPhoto = False
        hasShout = False
        photo_path = ""

        # Check Photo
        if d['photos']['count'] > 0:
            hasPhoto = True
            photo_path = get_photo(d['photos']['items'][0])
        
        # Check message
        if 'shout' in d:
            hasShout = True
        
        # memo: formattedAddress の末尾要素が郵便番号の時と、違う時がある。
        post_address = d['venue']['location']['formattedAddress'][-1] if not re.match(r'\d{3}-?\d{4}', d['venue']['location']['formattedAddress'][-1]) else d['venue']['location']['formattedAddress'][-2]

        # get checkinShortUrl
        url = f"https://api.foursquare.com/v2/checkins/{d['id']}"
        params = {
            'oauth_token': FORSQUARE_ACCESS_TOKEN,
            'v': '20231022',  # Foursquare APIのバージョンを指定
        }
        checkins_details_json = get_request(url)
        
        checkinShortUrl = checkins_details_json['response']['checkin']['checkinShortUrl']
        
        if hasShout:
            post_msg = f"{d['shout']} (@ {d['venue']['name']} in {post_address}) {checkinShortUrl}"
        else:
            post_msg = f"I'm at {d['venue']['name']} in {post_address} {checkinShortUrl}"

        print(f"{post_msg}, {hasPhoto}")

        tw_client_v2, tw_api_v1 = create_tw_client()
        mstdn_client = create_mstdn_client()
        if hasPhoto:
            media = tw_api_v1.media_upload(filename=photo_path)
            tw_client_v2.create_tweet(text=post_msg, media_ids=[media.media_id])
            media_files = [mstdn_client.media_post(photo_path, mimetypes.guess_type(photo_path)[0])]
            mstdn_client.status_post(status=post_msg, media_ids=media_files, visibility="private")
            os.remove(photo_path)
        else:
            tw_client_v2.create_tweet(text=post_msg)
            mstdn_client.status_post(status=post_msg, visibility="private")

        post_ids.append(d['id'])
        time.sleep(1)
    
    with open(LAST_POST_MEMO_PATH, 'a') as f:
        for l in post_ids:
            f.write(str(l) + "\n")
        f.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())