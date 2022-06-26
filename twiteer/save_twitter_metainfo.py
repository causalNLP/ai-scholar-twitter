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


def save_user_info(q, save_name, GS_ID, api):

    all_candidate = []
    # search the query
    users = api.search_users(q)

    for user in users:
        if user.followers_count > 10 and user.friends_count > 10:
            # json_object = json.dumps(user._json, indent=4, sort_keys=True)
            dic = user._json
            dic["GS_ID"] = GS_ID
            dic["GS_Name"] = q
            all_candidate.append(dic)

    newlist = sorted(all_candidate, key=lambda d: d['followers_count'], reverse=True)
    with jsonlines.open("./intermediate_data/" + save_name + ".jsonl", 'a') as writer:
        # csv_writer = csv.writer(writer)
        for each in newlist:
            # print(each)
            # csv_writer.writerow(each)
            writer.write(each)

    with jsonlines.open("./intermediate_data/" + save_name + ".csv", 'a') as writer:
        writer.write(GS_ID)



if __name__ == "__main__":
    import numpy as np
    total_info = np.load("meta_info.npy", allow_pickle=True)
    searched_dict = {}
    auth = get_auth("/cluster/home/zzhiheng/cogito/twitter_key/auth_1.json")
    auth2 = get_auth("/cluster/home/zzhiheng/cogito/twitter_key/auth_2.json")
    api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503]))
    api2 = tweepy.API(auth2, wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503]))
    with open("./intermediate_data/search_info.csv","r") as f:
        for i in f.readlines():
            searched_dict[i[1:-2]]=1
    print(len(searched_dict))
    for item in tqdm(range(len(total_info[0]))):
        if searched_dict.get(total_info[0][item])==1:
            continue
        try:
            save_user_info(total_info[1][item], "search_info", total_info[0][item], api)
        except:
            time.sleep(20)
            api, api2=api2, api
        time.sleep(2)
        searched_dict[item] = 1

    # with open("nlp_profile.csv", 'r') as csv_file:
    #     csv_reader = csv.reader(csv_file)
    #     for row in tqdm(csv_reader):
    #         if "/" not in row[0]:
    #             save_user_info(row[0])

    # print('\n')
    # twitter = Twitter(auth = OAuth(access_token, access_token_secret, consumer_key, consumer_secret))
    # search_result = twitter.users.search(q = q)
    # for user in search_result:
    #   print(user["screen_name"])