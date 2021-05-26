import requests
from requests_oauthlib import OAuth1Session
import json
import urllib
from .config import API_KEY, API_KEY_SECRET, BEARER,ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BOT_ID, BOT_HANDLE
# from threading import Thread
# import time

class Bot:
    def __init__(self):
        self.auth = OAuth1Session(API_KEY, client_secret=API_KEY_SECRET, resource_owner_key=ACCESS_TOKEN, resource_owner_secret=ACCESS_TOKEN_SECRET)
        self.headers = {'Authorization':'Bearer {}'.format(BEARER)}
        self.add_rules()

    def reply(self, reply_text, twt_id):
        p = self.auth.post("https://api.twitter.com/1.1/statuses/update.json",data={'status':reply_text,'in_reply_to_status_id':twt_id})
        if(p.status_code!=200):
            print(p.json())

    def retweet(self, twt_id):
        p = self.auth.post("https://api.twitter.com/1.1/statuses/retweet/{}.json".format(twt_id))
        if(p.status_code!=200):
            print(p.json())

    def dm(self, receiver_id, message):
        p = self.auth.post("https://api.twitter.com/1.1/direct_messages/events/new.json",data=json.dumps({"event":{"type":"message_create","message_create":{"target":{"recipient_id":"{}".format(receiver_id)},"message_data":{"text":"{}".format(message)}}}}))
        if(p.status_code!=200):
            print("error:{'Unable to send message'}")

    def search(self, queries, expansions=None, tweet_fields=None):
        queries = to_query_str(queries)
        if(not(expansions)):
            expansions = "author_id,geo.place_id,referenced_tweets.id"
        if(not(tweet_fields)):
            tweet_fields = "conversation_id,created_at,geo,referenced_tweets"
        s = requests.get("https://api.twitter.com/2/tweets/search/recent?query={}&max_results=100&expansions={}&tweet.fields={}&user.fields=location,description,username".format(queries,expansions,tweet_fields),headers=self.headers)
        return s.json()

    def stream(self,type="search"):
        print("STREAM STARTED! Listening ...\n")
        timeout = 0
        while True:
            try:
                # if(type=="covid"): # USE THIS ONLY AFTER TWITTER APPROVES OUR BOT
                #     def get_covid_data(self,partition):
                #         response = requests.get("https://api.twitter.com/labs/1/tweets/stream/covid19?partition={}".format(partition), headers=self.headers, stream=True)
                #         self.on_stream_trigger(response)
                #     threads = []
                #     for partition in range(1,5):
                #         Thread(target=get_covid_data,args=(self,partition,)).start()
                #     time.sleep(2**timeout*1000)
                #     timeout += 1
                if(type=="search"):
                    response = requests.get("https://api.twitter.com/2/tweets/search/stream?expansions=author_id", headers=self.headers, stream=True)
                    self.on_stream_trigger(response)
            except KeyboardInterrupt as e:
                print("\nSTREAM CLOSED!")
                raise SystemExit(e)
            except:
                continue

    def add_rules(self):
        rules = [{'value':"{} (-is:retweet)".format(BOT_HANDLE)}]
        payload = {"add":rules}
        r = requests.post("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers,json=payload)

    def delete_all_rules(self):
        r = requests.get("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers)
        rules = r.json()
        if(rules.get('data',None)):
            ids = list(map(lambda rule: rule["id"], rules["data"]))
            payload = {"delete": {"ids": ids}}
            response = requests.post("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers,json=payload)

    def on_stream_trigger(self,response):
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if(json_response['data']['author_id']!=BOT_ID):
                    # USE THIS ONLY AFTER TWITTER APPROVES OUR BOT
                    # self.reply("Hello World! This is Testing",int(json_response['data']['id']))
                    # for user in json_response['includes']['users']:
                    #     if(user['id']==json_response['data']['author_id']):
                    #         author_name = user['name']
                    #         break
                    # self.dm(json_response['data']['author_id'],"Hey {}!\nThanks for tagging us. Here are some supplies!".format(author_name))
                    print("{}\n".format(json_response))

def to_query_str(queries):
    http_safe = []
    for q in queries:
        http_safe.append(urllib.parse.quote(q))
    return "+AND+".join(http_safe)


def search_results2ids(search_results):
    statuses = search_results['statuses']
    ids = []
    for status in statuses:
        ids.append(status['id'])
    return ids


if __name__=="__main__":
    bot = Bot()
    bot.stream()
