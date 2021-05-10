#/usr/bin/python3
#Author: Pranav Sastry
#DateTime: 2021-05-04 22:41:44.450244 IST

import sys
import os
sys.path.append("/opt/anaconda3/lib/python3.7/site-packages/")
import requests
from requests_oauthlib import OAuth1Session
import json
import time
import datetime
import pytz

while True:
    curr_datetime_str = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M:%S')

    tweeting_status = open("twt_status.txt","r").read()
    new_job = tweeting_status.split('\n')[-2] #format - ON 10-05-2021 20:41:13

    new_job_split = new_job.split(' ')
    job_status = new_job_split[0]
    job_datetime_str = new_job_split[1]+" "+new_job_split[2]

    if((job_status=='ON') and (job_datetime_str==curr_datetime_str)):
        print("Started {}".format(curr_datetime_str))
        consumer_key = os.getenv('TWT_COVID_API')
        consumer_secret = os.getenv('TWT_COVID_API_SECRET')
        bearer_token = os.getenv('TWT_BEARER')
        access_token = os.getenv('TWT_ACCESS')
        access_token_secret = os.getenv('TWT_ACCESS_SECRET')

        header = {"Authorization": "Bearer {}".format(bearer_token)}

        twt = OAuth1Session(consumer_key,client_secret=consumer_secret,resource_owner_key=access_token,resource_owner_secret=access_token_secret)
        get_twts_url = "https://api.twitter.com/1.1/search/tweets.json?q=%23SOSBangalore+OR+%23BangaloreSOS+OR+%23CovidBangalore+OR+%23CovidBengaluru&count=50&result_type=recent"
        r = requests.get(get_twts_url,headers=header)
        twt_json_obj = r.json()
        twt_status = twt_json_obj['statuses']
        for status in twt_status:
            if(status['user']['name']!="COVID_BLR_BOT"):
                p = twt.post("https://api.twitter.com/1.1/statuses/retweet/{}.json".format(status['id']))
                # print(p.json())
                time.sleep(2)
        print("Done {}".format(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M:%S')))
