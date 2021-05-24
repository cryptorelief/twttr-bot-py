from config import API_KEY, API_KEY_SECRET, BEARER,ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BOT_ID, BOT_HANDLE
import requests
from requests_oauthlib import OAuth1Session
import json

class Bot:
    def __init__(self):
        self.auth = OAuth1Session(API_KEY, client_secret=API_KEY_SECRET, resource_owner_key=ACCESS_TOKEN, resource_owner_secret=ACCESS_TOKEN_SECRET)
        self.headers = {'Authorization':'Bearer {}'.format(BEARER)}

    def reply(self, reply_text, twt_id):
        p = self.auth.post("https://api.twitter.com/1.1/statuses/update.json",data={'status':reply_text,'in_reply_to_status_id':twt_id})
        if(p.status_code!=200):
            print(p.json())

    def retweet(self, twt_id):
        p = self.auth.post("https://api.twitter.com/1.1/statuses/retweet/{}.json".format(twt_id))
        if(p.status_code!=200):
            print(p.json())

    def search(self, queries, num_tweets, result_type):
        queries = to_query_str(queries)
        s = requests.get("https://api.twitter.com/1.1/search/tweets.json", data={'q':queries,'count':num_tweets,'result_type':result_type}, headers=self.headers)
        return s.json()

    def stream(self):
        self.add_rules()
        print("STREAM STARTED! Listening ...\n")
        while True:
            try:
                with requests.get("https://api.twitter.com/2/tweets/search/stream?expansions=author_id", headers=self.headers, stream=True) as response:
                    for line in response.iter_lines():
                        if line:
                            json_response = json.loads(line)
                            if(json_response['data']['author_id']!=BOT_ID):
                                self.retweet(int(json_response['data']['id']))
                                # USE THIS ONLY AFTER TWITTER APPROVES OUR BOT
                                # self.reply("Hello World! This is Testing",int(json_response['data']['id']))
                                print("{}\n".format(json_response))
            except KeyboardInterrupt as e:
                print("\nSTREAM CLOSED!")
                raise SystemExit(e)
            except:
                continue

    def add_rules(self):
        rules = [{'value':"{} (-is:retweet -is:quote -is:reply)".format(BOT_HANDLE)}]
        payload = {"add":rules}
        r = requests.post("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers,json=payload)

    def delete_all_rules(self):
        r = requests.get("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers)
        rules = r.json()
        if(rules.get('data',None)):
            ids = list(map(lambda rule: rule["id"], rules["data"]))
            payload = {"delete": {"ids": ids}}
            response = requests.post("https://api.twitter.com/2/tweets/search/stream/rules",headers=self.headers,json=payload)

def to_query_str(queries):
    for q in queries:
        q = q.replace("#","%23")
        q = q.replace("@","%40")
    return "+OR+".join(queries)


def search_results2ids(search_results):
    statuses = search_results['statuses']
    ids = []
    for status in statuses:
        ids.append(status['id'])
    return ids


if __name__=="__main__":
    bot = Bot()
    bot.stream()
