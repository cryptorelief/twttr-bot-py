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


def get_data(fname):
    if(fname=="extracted_data"):
        file_obj = open("bot/scraper/extracted_data.json","r")
    elif(fname=="hashed_data"):
        file_obj = open("bot/scraper/hashed_data.json","r")
    data = json.load(file_obj)['data']
    file_obj.close()
    return data


def save_to_file(data,fname):
    if(fname=="extracted_data"):
        file_obj = open("bot/scraper/extracted_data.json","w")
    elif(fname=="hashed_data"):
        file_obj = open("bot/scraper/hashed_data.json","w")
    json.dump({"data":data},file_obj,indent=4,default=str)
    file_obj.close()


def scrape(bot, num_tweets, queries):
    print("SCRAPING ...\n")
    tweets_scraped = 0
    extracted_data = []
    hashed_data = get_data("hashed_data")
    while(tweets_scraped<num_tweets):
        try:
            search_results = bot.search(queries=queries)['data'] # 100 is the max you can fetch from Twitter at a time
            for result in search_results:
                result_hash = sha256(str(result).encode('utf-8')).hexdigest()
                if(result_hash not in hashed_data):
                    extracted_data.append(result)
                    hashed_data.append(result_hash)
                    tweets_scraped += 1
                    print("\r{} / {} tweets scraped!".format(tweets_scraped,num_tweets),end="")
                    if(tweets_scraped==num_tweets):
                        break
            if(tweets_scraped==num_tweets):
                break
            time.sleep(5) # Time delay to make sure that our bot doesn't get banned
        except KeyboardInterrupt as e:
            save_to_file(extracted_data,"extracted_data")
            save_to_file(hashed_data,"hashed_data")
            raise SystemExit(e)
        except KeyError:
            continue
    save_to_file(extracted_data,"extracted_data")
    save_to_file(hashed_data,"hashed_data")
    print("\n\nDONE")


if __name__=="__main__":
    try:
        num_tweets = int(sys.argv[1])
    except IndexError:
        print("ERROR \n Enter the number of tweets to be scraped as Command line argument (int)!")
        raise SystemExit
    scrape(bot=Bot(), num_tweets=num_tweets, queries=["lang:en (#COVIDEmergency2021 OR #AmphotericinB OR #CovidSOS OR #LiposomalAmphotericin OR #LiposomalAmphotericinB OR #Tocilizumab400 OR @COVResourcesIn OR @IndiaCovidRes OR @COVIDCitizens OR @TeamSOSIndia) (-is:retweet)"])
