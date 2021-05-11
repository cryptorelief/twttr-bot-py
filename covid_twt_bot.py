#/usr/bin/python3
#Author: Pranav Sastry
#DateTime: 2021-05-04 22:41:44.450244 IST

import sys
import os
sys.path.append("/opt/anaconda3/lib/python3.7/site-packages/")
import requests
from requests_oauthlib import OAuth1Session
import json
import datetime
import pytz
import time
from flask import Flask

app = Flask(__name__)

def twttr_bot():
    print("Job started! {}".format(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%YT%H:%M:%S')))

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
            #reply_text = "%40{} Contact us on WhatsApp wa.me/12345178991?te…".format(status['user']['screen_name'])
            #q = twt.post("https://api.twitter.com/1.1/statuses/update.json?status={}&in_reply_to_status_id={}".format(reply_text,status['id']))
            # print(p.json())
            time.sleep(1)
    print("Job executed! {}".format(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%YT%H:%M:%S')))

# GET all jobs
@app.route("/jobs",methods=["GET"])
def get_jobs():
    twt_status_file = open("twt_status.json")
    twt_status = json.load(twt_status_file)
    twt_status_file.close()
    return twt_status,200

# GET a job
@app.route("/jobs/<job_id>",methods=["GET"])
def get_job(job_id):
    twt_status_file = open("twt_status.json")
    twt_status = json.load(twt_status_file)["data"]
    twt_status_file.close()
    for status in twt_status:
        if status["job_id"]==job_id:
            return status,200
        else:
            return {"error":"Job with the given job_id not found!"},404

# PUT / Create a new job
@app.route("/jobs/<job_status>/<job_date_time>",methods=["PUT"])
def put_job(job_status,job_date_time):
    twt_status_file = open("twt_status.json")
    twt_status = json.load(twt_status_file)["data"]
    twt_status_file.close()
    new_job = {"job_id":str(len(twt_status)+1),"job_status":job_status,"job_date_time":job_date_time}
    twt_status.append(new_job)
    twt_status_json = {"data":twt_status}
    twt_status_file = open("twt_status.json","w")
    json.dump(twt_status_json,twt_status_file,indent=4)
    twt_status_file.close()
    return new_job,200

# POST / Run a job
@app.route("/jobs/<job_id>",methods=["POST"])
def post_job(job_id):
    twttr_bot()
    return {"success":"Job executed!"},200

# DELETE a job
@app.route("/jobs/<job_id>",methods=["DELETE"])
def delete_job(job_id):
    twt_status_file = open("twt_status.json")
    twt_status = json.load(twt_status_file)["data"]
    twt_status_file.close()
    idx = 0
    for status in twt_status:
        if(status["job_id"]==job_id):
            del twt_status[idx]
            twt_status_json = {"data":twt_status}
            twt_status_file = open("twt_status.json","w")
            json.dump(twt_status_json,twt_status_file,indent=4)
            twt_status_file.close()
            return status,200
        idx+=1
    return {"error":"Job with the given job_id not found!"},404

# DELETE all jobs
@app.route("/jobs",methods=["DELETE"])
def delete_jobs():
    twt_status_json = {"data":[]}
    twt_status_file = open("twt_status.json","w")
    json.dump(twt_status_json,twt_status_file,indent=4)
    twt_status_file.close()
    return "Deleted all jobs!",200

if __name__=='__main__':
    app.run(debug=True)
