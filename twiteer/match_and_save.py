import re
import tweepy
from twitter import *
import requests
import json
import csv
import jsonlines
import time
from tqdm import tqdm
import numpy as np
from icecream import ic

from get_auth import get_auth, API_controler
from save_tweets import get_tweets, get_tweets_simple, get_tweets_simple_qnqq, get_tweets_qnqq
from sketch_match import match_single_author


# Save tweets
if __name__ == "__main__":
    GS_info_path = "/cluster/project/sachan/zhiheng/twiteer/meta_info.npy"
    supplement_GS_info_path = "/cluster/project/sachan/zhiheng/twiteer/data_from_GS/GS_info_beta.npy"
    search_info_path = "/cluster/project/sachan/zhiheng/twiteer/intermediate_data/search_info.jsonl"
    tweets_save_path = "/cluster/project/sachan/zhiheng/twiteer/final_output/tweets_data_website_matching.jsonl"
    GS_save_path = "/cluster/project/sachan/zhiheng/twiteer/final_output/GS_data_website_matching.jsonl"

    tweets_dict = {}
    with jsonlines.open(tweets_save_path, 'r') as reader:
        for i in reader:
            tweets_dict[i["screen_name"]] = 1
    print("Finish load screen_name")
    auth = get_auth("/cluster/home/zzhiheng/cogito/twitter_key/auth_1.json")
    auth2 = get_auth("/cluster/home/zzhiheng/cogito/twitter_key/auth_2.json")
    auth3 = get_auth("/cluster/home/zzhiheng/cogito/twitter_key/auth_3.json")
    auth4 = get_auth("/cluster/home/zzhiheng/cogito/twitter_key/auth_4.json")
    apis = API_controler()
    apis.add_api(tweepy.API(auth, wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503])))
    apis.add_api(tweepy.API(auth2, wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503])))
    apis.add_api(tweepy.API(auth3, wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503])))
    apis.add_api(tweepy.API(auth4, wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503])))
    api = apis.change_api()

    GS_info = np.load(GS_info_path, allow_pickle=True)
    GS_info_dict = {}
    for i in range(len(GS_info[0])):
        id = GS_info[1][i]
        GS_info_dict[id] = {
            "name":GS_info[0][i],
            "id":GS_info[1][i],
            "extra_info":GS_info[2][i],
            "personal_webpage":GS_info[3][i],
        }
    supplement_GS_info = np.load(supplement_GS_info_path, allow_pickle=True)
    for i in supplement_GS_info:
        id = i.get('url').split("user=")[-1]
        if (GS_info_dict.get(id)==None):
            GS_info_dict[id] = i

    current_time = 0
    import time
    last_time = time.time()
    with jsonlines.open(search_info_path, 'r') as reader:
        now_id = ""
        candidate_list = []
        for each_candidate in reader:
            # 提取连续的一串相同id
            if each_candidate["GS_ID"] != now_id:
                GS_author_dict = {}
                GS_author_dict["id"] = now_id
                GS_author_dict["screen_name_list"] = []
                GS_author_dict["matched_type"] = []

                if (len(candidate_list)!=0):
                    matched_list = []
                    if (GS_info_dict.get(now_id)!=None):
                        GS_info_now = GS_info_dict[now_id]
                        for i in candidate_list:
                            if match_single_author(GS_info_now, i)>0:
                                matched_list.append([i, match_single_author(GS_info_now, i)])
                    if (len(matched_list) == 0):
                        GS_author_dict["is_matched"] = False
                        for i in candidate_list:
                            screeen_name = i["screen_name"]
                            if (tweets_dict.get(screeen_name) != None):
                                continue
                            GS_author_dict["screen_name_list"].append(screeen_name)
                            GS_author_dict["matched_type"].append(0)
                            tweets_list = get_tweets_simple_qnqq(screeen_name, api)
                            if (tweets_list == None):
                                api = apis.change_api()
                            else:
                                current_time += 1
                                if current_time % 100 == 0:
                                    print(f"time usage: {time.time() - last_time}")
                                    last_time = time.time()
                                with jsonlines.open(tweets_save_path, 'a') as writer:
                                    writer.write({"screen_name":screeen_name,"tweets":tweets_list})
                                del tweets_list
                                tweets_dict[screeen_name] = 1
                    else:
                        GS_author_dict["is_matched"] = True
                        for i in matched_list:
                            screeen_name = i[0]["screen_name"]
                            if (tweets_dict.get(screeen_name) != None):
                                continue
                            GS_author_dict["screen_name_list"].append(screeen_name)
                            GS_author_dict["matched_type"].append(i[1])
                            tweets_list = get_tweets_qnqq(screeen_name, api)
                            if (tweets_list == None):
                                api = apis.change_api()
                            else:
                                current_time += 1
                                if current_time % 100 == 0:
                                    print(f"time usage: {time.time() - last_time}")
                                    last_time = time.time()
                                with jsonlines.open(tweets_save_path, 'a') as writer:
                                    writer.write({"screen_name":screeen_name,"tweets":tweets_list})
                                del tweets_list
                                tweets_dict[screeen_name] = 1

                with jsonlines.open(GS_save_path, 'a') as writer:
                    writer.write(GS_author_dict)

                del GS_author_dict
                del candidate_list
                candidate_list = [each_candidate]
                now_id = each_candidate["GS_ID"]
            else:
                candidate_list.append(each_candidate)
