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
from pandas import DataFrame
from collections import Counter


def load_jsonl_list(path):
    jsonl_list = []
    with jsonlines.open(path, 'r') as reader:
        for i in reader:
            jsonl_list.append(dict(i))
    return jsonl_list

# The input is (list1, list2)
# The output is {screen:(GS_ID, matched_type)}
def get_project_dict(GS_list):
    project_dict = {}
    badcase_during_project = 0
    no_matched = 0
    sum = 0
    matched = []
    for i in GS_list:
        sum+=1
        if (i.get("is_matched")==None):
            no_matched+=1
            ic(i)
            continue
        if (not i['is_matched']):
            continue
        GS_id = i['id']
        for j in range(len(i['screen_name_list'])):
            if (project_dict.get(i['screen_name_list'][j])!=None and project_dict.get(i['screen_name_list'][j])[0]!=GS_id):
                badcase_during_project += 1
                if (project_dict.get(i['screen_name_list'][j])[1]<i["matched_type"][j] or project_dict.get(i['screen_name_list'][j])[1]==1):
                    ic(project_dict.get(i['screen_name_list'][j]), (GS_id, i["matched_type"][j]), i['screen_name_list'][j])
                    continue
            project_dict[i['screen_name_list'][j]] = (GS_id, i["matched_type"][j])
            matched.append(i["matched_type"][j])
    ic(Counter(matched))
    ic(sum)
    ic(no_matched)
    ic(badcase_during_project)
    return project_dict

#
def create_correspondent_CSV(project_dict, twitter_path, output_dir):
    badcase_during_generate_dataset = 0
    final_dict = {
        "id":[],
        "full_text":[],
        "num_of_likes":[],
        "retweeted_status":[],
        "user_description":[],
        "user_followers_count":[],
        "user_friends_count":[],
        "screen_name":[],
        "GS_ID":[],
        "matched_type":[],
        "time_stamp":[],
    }
    sum = 0

    import json
    path1 = r""  # 文件的存储位置
    with open(twitter_path, 'r') as f:
        try:
            while True:
                line_data = f.readline()
                if line_data:
                    data = json.loads(line_data)
                    sum += 1
                    if (sum % 100 == 0 or sum<10):
                        ic(sum)
                    twitter = dict(data)
                    screen_name = twitter["screen_name"]

                    if (project_dict.get(screen_name) == None):
                        badcase_during_generate_dataset += 1
                        continue
                    GS_ID, matched_type = project_dict.get(screen_name)
                    for tweets in twitter["tweets"]:
                        if (tweets.get("retweeted_status") != None):
                            retweeted_status = 1
                            full_text = tweets.get("retweeted_status")["full_text"]
                            num_of_likes = tweets.get("retweeted_status")["favorite_count"]
                        else:
                            retweeted_status = 0
                            full_text = tweets['full_text']
                            num_of_likes = tweets["favorite_count"]
                        id = tweets['id']
                        time_stamp = tweets['created_at']
                        user = tweets.get("user")
                        user_description = user.get("description")
                        user_followers_count = user.get("followers_count")
                        user_friends_count = user.get("friends_count")
                        final_dict["id"].append(id)
                        final_dict["time_stamp"].append(time_stamp)
                        final_dict["full_text"].append(full_text)
                        final_dict["num_of_likes"].append(num_of_likes)
                        final_dict["retweeted_status"].append(retweeted_status)
                        final_dict["user_description"].append(user_description)
                        final_dict["user_followers_count"].append(user_followers_count)
                        final_dict["user_friends_count"].append(user_friends_count)
                        final_dict["screen_name"].append(screen_name)
                        final_dict["GS_ID"].append(GS_ID)
                        final_dict["matched_type"].append(matched_type)
                else:
                    break
        except Exception as e:
            print(e)
            f.close()
    ic(badcase_during_generate_dataset)
    ic(Counter(final_dict["matched_type"]))
    df = DataFrame.from_dict(final_dict)
    df.to_csv(output_dir)


if __name__ == "__main__":
    GS_path = "/cluster/project/sachan/zhiheng/twiteer/final_output/GS_data_website_matching.jsonl"
    tweets_path = "/cluster/project/sachan/zhiheng/twiteer/final_output/tweets_data_website_matching.jsonl"
    output_dir = "/cluster/project/sachan/zhiheng/twiteer/final_output/tweets_dataset_update0525.csv"

    GS_list = load_jsonl_list(GS_path)
    project_dict = get_project_dict(GS_list)
    create_correspondent_CSV(project_dict, tweets_path, output_dir)



