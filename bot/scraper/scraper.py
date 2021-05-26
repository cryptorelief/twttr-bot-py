import os
import sys
from hashlib import sha256
import json
import time

from ..src.bot import Bot

def hash_data(data):
    hashed = []
    for d in data:
        hashed.append(sha256(str(d).encode('utf-8')).hexdigest())
    return hashed


def get_extracted_data():
    file_obj = open("bot/scraper/extracted_data.json","r")
    data = json.load(file_obj)['data']
    file_obj.close()
    return data


def save_to_file(data):
    file_obj = open("bot/scraper/extracted_data.json","w")
    json.dump({"data":data},file_obj,indent=4,default=str)
    file_obj.close()


def scrape(bot, num_tweets, queries):
    print("SCRAPING ...\n")
    tweets_scraped = 0
    extracted_data = get_extracted_data()
    while(tweets_scraped<=num_tweets):
        hashed_extracted_data = hash_data(extracted_data)
        try:
            search_results = bot.search(queries=queries)['data'] # 100 is the max you can fetch from Twitter at a time
        except KeyboardInterrupt as e:
            raise SystemExit(e)
        except KeyError:
            continue
        for result in search_results:
            result_hash = sha256(str(result).encode('utf-8')).hexdigest()
            if(result_hash not in hashed_extracted_data):
                extracted_data.append(result)
                tweets_scraped += 1
                print("\r{} / {} tweets scraped!".format(tweets_scraped,num_tweets),end="")
                if(tweets_scraped==num_tweets):
                    break
        if(tweets_scraped==num_tweets):
            break
        time.sleep(30) # Time delay to make sure that our bot doesn't get banned
    save_to_file(extracted_data)
    print("\n\nDONE")


if __name__=="__main__":
    try:
        num_tweets = int(sys.argv[1])
    except IndexError:
        print("ERROR \n Enter the number of tweets to be scraped as Command line argument (int)!")
        raise SystemExit
    scrape(bot=Bot(), num_tweets=num_tweets, queries=["lang:en (#COVIDEmergency2021 OR #AmphotericinB OR #CovidSOS OR #LiposomalAmphotericin OR #LiposomalAmphotericinB OR #Tocilizumab400 OR @COVResourcesIn OR @IndiaCovidRes OR @COVIDCitizens OR @TeamSOSIndia) (-is:retweet)"])
