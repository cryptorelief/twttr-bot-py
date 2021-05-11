import json
import datetime
import pytz
import requests

base_url = "http://127.0.0.1:5000/"

twt_status_file = open("twt_status.json")
twt_status = json.load(twt_status_file)["data"]
twt_status_file.close()

next_job = twt_status[-1] # Gets the last job in the list
job_status = next_job["job_status"]
job_date_time = next_job["job_date_time"]
job_id = next_job["job_id"]

if(len(twt_status)!=0):
    while True:
        curr_datetime_str = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%YT%H:%M:%S')
        if((job_status=='ON') and (job_date_time==curr_datetime_str)):
            requests.post("{}jobs/{}".format(base_url,job_id))
            break
