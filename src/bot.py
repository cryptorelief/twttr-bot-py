import requests
from requests_oauthlib import OAuth1Session
import json
import urllib
from src.config import API_KEY, API_KEY_SECRET, BEARER,ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BOT_ID, BOT_HANDLE
import logging
from requests.exceptions import ChunkedEncodingError
# from threading import Thread
# import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s]: [%(levelname)s]: %(name)s:  %(message)s ","%d-%m-%Y %H:%M:%S")
file_handler = logging.FileHandler('src/bot.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class Bot:
    def __init__(self):
        logger.info("Bot STARTED.")
        self.auth = OAuth1Session(API_KEY, client_secret=API_KEY_SECRET, resource_owner_key=ACCESS_TOKEN, resource_owner_secret=ACCESS_TOKEN_SECRET)
        self.headers = {'Authorization':'Bearer {}'.format(BEARER)}
        self.add_rules()

    def tweet(self,text):
        messages = split_text(text,f"@{BOT_HANDLE} ")
        p = self.auth.post("https://api.twitter.com/1.1/statuses/update.json",data={'status':messages[0]})
        if(p.status_code!=200):
            logger.error(f"Tweet {p.json()}")
            return
        twt_id, twt_author = self.get_tweet_details(p.json())
        for message in messages[1:]:
            p = self.auth.post("https://api.twitter.com/1.1/statuses/update.json",data={'status':f"@{twt_author} "+message,'in_reply_to_status_id':twt_id})
            if(p.status_code!=200):
                logger.error(f"Tweet {p.json()}")
                return
            twt_id, twt_author = self.get_tweet_details(p.json())

    def reply(self, text, tweet_id, tweet_author):
        twt_id = tweet_id
        twt_author = tweet_author
        handle_str = f"@{twt_author} "
        messages = split_text(text,handle_str)
        for message in messages:
            p = self.auth.post("https://api.twitter.com/1.1/statuses/update.json",data={'status':handle_str+message,'in_reply_to_status_id':twt_id})
            if(p.status_code!=200):
                logger.error(f"Reply {p.json()}")
                return
            twt_id, twt_author = self.get_tweet_details(p.json())

    def retweet(self, twt_id):
        p = self.auth.post("https://api.twitter.com/1.1/statuses/retweet/{}.json".format(twt_id))
        if(p.status_code!=200):
            logger.error(f"Retweet {p.json()}")

    def dm(self, receiver_id, message):
        p = self.auth.post("https://api.twitter.com/1.1/direct_messages/events/new.json",data=json.dumps({"event":{"type":"message_create","message_create":{"target":{"recipient_id":"{}".format(receiver_id)},"message_data":{"text":"{}".format(message)}}}}))
        if(p.status_code!=200):
            logger.error(f"DM {p.json()}")

    def search(self, queries, expansions=None, tweet_fields=None):
        queries = to_query_str(queries)
        if(not(expansions)):
            expansions = "author_id,geo.place_id,referenced_tweets.id"
        if(not(tweet_fields)):
            tweet_fields = "conversation_id,created_at,geo,referenced_tweets"
        s = requests.get("https://api.twitter.com/2/tweets/search/recent?query={}&max_results=100&expansions={}&tweet.fields={}&user.fields=location,description,username".format(queries,expansions,tweet_fields),headers=self.headers)
        if(s.status_code!=200):
            logger.error(f"Search {s.json()}")
            return None
        else:
            return s.json()

    def stream(self,type="search"):
        print("STREAM STARTED! Listening ...\n")
        timeout = 0
        while True:
            try:
                # if(type=="covid"): # USE THIS ONLY AFTER TWITTER APPROVES OUR BOT
                #     def get_covid_data(self,partition):
                #         response = requests.get("https://api.twitter.com/labs/1/tweets/stream/covid19?partition={}".format(partition), headers=self.headers, stream=True)
                #         if(response.status_code!=200):
                #             logger.error(f"CovidStream {response.json()}")
                #             break
                #         self.on_stream_trigger(response)
                #     threads = []
                #     for partition in range(1,5):
                #         Thread(target=get_covid_data,args=(self,partition,)).start()
                #     time.sleep(2**timeout*1000)
                #     timeout += 1
                if(type=="search"):
                    response = requests.get("https://api.twitter.com/2/tweets/search/stream?expansions=author_id", headers=self.headers, stream=True)
                    if(response.status_code!=200):
                        logger.error(f"SearchStream {response.json()}")
                        break
                    self.on_stream_trigger(response)
            except KeyboardInterrupt as e:
                print("\nSTREAM CLOSED!")
                raise SystemExit(e)
            except ChunkedEncodingError:
                continue
            except Exception as e:
                logger.exception(f"STREAMING {e}")
                raise

    def get_location_data(self,place_id):
        r = requests.get(f"https://api.twitter.com/1.1/geo/id/:{place_id}.json",headers=self.headers)
        if(r.status_code!=200):
            logger.error(f"GetLocation {r.json()}")
            return None
        else:
            r_json = r.json()
            if(r_json['place_type']!='city'):
                found = False
                for place in r_json['contained_within']:
                    if(place['place_type']=='city'):
                        found = True
                        return place['name']
                if(not(found)):
                    return None
            else:
                return r_json['name']

    def get_tweet_details(self,request_json):
        twt_id = request_json['id']
        twt_author = request_json['user']['screen_name']
        return twt_id,twt_author

    def add_rules(self):
        rules = [{'value':"{} (-is:retweet)".format(BOT_HANDLE)}]
        payload = {"add":rules}
        r = requests.post("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers,json=payload)
        if(r.status_code!=200):
            r_str = json.dumps(r.json())
            if('DuplicateRule' not in r_str):
                logger.error(f"AddRules {r.json()}")

    def delete_all_rules(self):
        r = requests.get("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers)
        rules = r.json()
        if(rules.get('data',None)):
            ids = list(map(lambda rule: rule["id"], rules["data"]))
            payload = {"delete": {"ids": ids}}
            r = requests.post("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers,json=payload)
            if(r.status_code!=200):
                logger.error(f"DeleteRules {r.json()}")

    def on_stream_trigger(self,response):
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if(json_response['data']['author_id']!=BOT_ID):
                    has_location = json_response.get('geo')
                    if(has_location):
                        location = self.get_location_data(has_location['place_id'])
                    # USE THIS ONLY AFTER TWITTER APPROVES OUR BOT
                    # self.retweet(int(json_response['data']['id']))
                    for user in json_response['includes']['users']:
                        if(user['id']==json_response['data']['author_id']):
                            author_name = user['name']
                            author_handle = user['username']
                            break
                    # self.reply("Thanks for tagging us. We'll get back with the latest supplies for you!",int(json_response['data']['id']),author_handle)
                    # self.dm(json_response['data']['author_id'],"Hey {}!\nThanks for tagging us. Here are some supplies!".format(author_name))
                    print("{}\n".format(json_response))

def to_query_str(query):
    return urllib.parse.quote(query)

def split_text(text,handle_str=None,limit=280):
    if(handle_str):
        limit -= len(handle_str)
    split_text_list = []
    words = text.split(" ")
    new_str = ""
    for (i,word) in enumerate(words):
        if(len(new_str+word+" ")<limit):
            new_str += (word + " ")
            if(i==len(words)-1):
                split_text_list.append(new_str)
        else:
            split_text_list.append(new_str)
            new_str = ""
    return split_text_list



if __name__=="__main__":
    bot = Bot()
    bot.stream()
