import re
import tweepy
from twitter import *
import requests
import json
import csv
import jsonlines
import time
from tqdm import tqdm
from get_auth import get_auth
import time

def get_tweets_simple(twitter_name, api):
    try:
        tweets = api.user_timeline(screen_name=twitter_name, count=10, tweet_mode="extended")
        tweets_list = []
        for tweet in tweets:
            json_object = tweet._json
            tweet_info = {"tweet_id": json_object["id"], "num_of_likes": json_object["favorite_count"],
                          "text": json_object["full_text"]}
            # get full text from retweets
            if "retweeted_status" in json_object:
                tweet_info = {"tweet_id": json_object["id"], "num_of_likes": json_object["favorite_count"],
                              "text": json_object["retweeted_status"]["full_text"]}
            # change the form of link in the tweets
            urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', tweet_info["text"])
            for each in urls:
                try:
                    r = requests.get(each)
                    tweet_info["text"] = tweet_info["text"].replace(each, r.url)
                except:
                    continue
            tweets_list.append(tweet_info)
        return tweets_list
    except:
        return None


def get_tweets_simple_qnqq(twitter_name, api):
    try:
        tweets = api.user_timeline(screen_name=twitter_name, count=10, tweet_mode="extended")
        tweets_list = []
        for tweet in tweets:
            json_object = tweet._json
            tweets_list.append(json_object)
        return tweets_list
    except:
        return None

def get_tweets_qnqq(twitter_name, api):
    try:
        tweets = api.user_timeline(screen_name=twitter_name, count=100, tweet_mode="extended")
        tweets_list = []
        for tweet in tweets:
            json_object = tweet._json
            tweets_list.append(json_object)
        return tweets_list
    except:
        return None

def get_tweets(twitter_name, api):
    current_time = time.time()
    try:
        tweets = api.user_timeline(screen_name=twitter_name, count=300, tweet_mode="extended")
        print(f"time crawing one tweets is {time.time()-current_time}")
        current_time = time.time()
        tweets_list = []
        for tweet in tweets:
            json_object = tweet._json
            tweet_info = {"tweet_id": json_object["id"], "num_of_likes": json_object["favorite_count"],
                          "text": json_object["full_text"]}
            # get full text from retweets
            if "retweeted_status" in json_object:
                tweet_info = {"tweet_id": json_object["id"], "num_of_likes": json_object["favorite_count"],
                              "text": json_object["retweeted_status"]["full_text"]}
            # change the form of link in the tweets
            urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', tweet_info["text"])
            for each in urls:
                try:
                    r = requests.get(each)
                    tweet_info["text"] = tweet_info["text"].replace(each, r.url)
                except:
                    continue
            tweets_list.append(tweet_info)
        print(f"time processing one tweets is {time.time()-current_time}")
        return tweets_list
    except:
        return None

def get_full_tweets(twitter_name, api):
    pass

if __name__ == "__main__":
    import numpy as np
    total_info = np.load("./data_from_GS/base_info_clean.npy", allow_pickle=True)
    searched_dict = {}
    auth = get_auth("./auth_2.json")
    api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503]))
    for i in tqdm(range(100)):
        get_tweets("aarnilmari", api)
        time.sleep(1)
