from sys import meta_path
import tweepy
import csv
import requests
import os
from deepface import DeepFace
from twitter import *
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm
from icecream import ic
import re
import jsonlines
import json

def download_profile_image(name, img_link):
    img_link = img_link.replace("normal", "400x400")
    if "default_profile_images" in img_link:
        return False
    if img_link:
        response = requests.get(img_link)

        file = open("./temp_pictures/" + name + '.jpg', "wb")
        file.write(response.content)
        return True
    # img_link is empty
    return False
    # homepage_link = user_info.url


def compare_two_images(img1, img2):
    try:
        result = DeepFace.verify(img1, img2)
        if result["distance"] < 0.25:
            return True
        return False
    except:
        return False
    # return result["verified"]


def whether_same_image(img1, img2):
    # https://deepai.org/machine-learning-model/image-similarity
    r = requests.post(
        "https://api.deepai.org/api/image-similarity",
        files={
            'image1': open(img1, 'rb'),
            'image2': open(img2, 'rb'),
        },
        headers={'api-key': '8d00045d-7b5b-4b84-969f-f96d79a4a94c'}
    )
    # print(r.json())
    if r.json()["output"]["distance"] == 0:
        return True
    return False

# 有用的
def match_by_meta_description(str1, str2):
    corpus = [str1, str2]
    token = RegexpTokenizer(r'[a-zA-Z0-9]+')
    count_vectorizer = CountVectorizer(ngram_range=(1, 1), tokenizer=token.tokenize)
    # ic(corpus, count_vectorizer)
    # if corpus:
    #     return False
    vec = count_vectorizer.fit_transform(corpus)
    score = cosine_similarity(vec, vec)[0][1]
    # print(score)
    #ic(corpus, score)
    if score > 0.399:
        return True
    return False


def get_keywords():
    field_names = ['natural language processing', 'computer vision', 'machine learning', 'artificial intelligence',
                   'deep learning', 'reinforcement learning', 'CV', 'NLP', 'AI', 'RL', 'GAN']
    role_names = ['researcher', 'research scientist', 'professor', 'Prof ', 'computational linguist']
    org_names = ['university']
    misc_names = ['#NLProc']
    additional_field_names = []
    for field in field_names:
        abbrev = ""
        for word in field.split():
            abbrev += word[0]

        additional_field_names += [field.replace(' ', '_'), field.replace(' ', ''), abbrev]
    field_names += additional_field_names
    keywords = field_names + role_names + org_names + misc_names
    return keywords


def if_keyword_match(text, keywords):
    text_lower = text.lower().split()
    return any(i in text_lower for i in keywords)


def match_by_homepage_link(str1, str2):
    corpus = [str1, str2]
    token = RegexpTokenizer(r'[a-zA-Z0-9]+')
    count_vectorizer = CountVectorizer(ngram_range=(1, 1), tokenizer=token.tokenize, stop_words='english')
    vec = count_vectorizer.fit_transform(corpus)
    score = cosine_similarity(vec, vec)[0][1]
    # print(score)
    if score > 0.9:
        return True
    return False


def match_by_tweets_arXiv(twitter_name):
    if os.path.exists("./saved_user_tweets/" + twitter_name + ".csv"):
        with open("./saved_user_tweets/" + twitter_name + ".csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for each_line in csv_reader:
                text = each_line[3]
                urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', text)
                for each in urls:
                    try:
                        r = requests.get(each)
                        text = text.replace(each, r.url)
                    except:
                        continue
                if "arXiv" in text:
                    return True
        return False
    return False
    # try:
    #   tweets = api.user_timeline(screen_name=twitter_name, count=100, tweet_mode="extended", wait_on_rate_limit=True, retry_count=10, retry_delay=5, retry_errors=set([503]))
    #   with open("./saved_user_tweets/" + twitter_name + ".csv", "w") as csv_file:
    #     # csv_writer = csv.writer(csv_file)
    #     csv_writer = csv.DictWriter(csv_file, fieldnames=["tweet_id", "num_of_likes", "text"])
    #     for tweet in tweets:
    #       json_object = tweet._json
    #       tweet_info = {"tweet_id": json_object["id"], "num_of_likes": json_object["favorite_count"], "text": json_object["full_text"]}
    #       if "retweeted_status" in json_object:
    #         tweet_info = {"tweet_id": json_object["id"], "num_of_likes": json_object["favorite_count"], "text": json_object["retweeted_status"]["full_text"]}
    #   #     csv_writer.writerow(tweet_info)
    #   # with open(twitter_name + ".jsonl", 'w') as jsonl_file:
    #   #   for tweet in user_tweets:
    #   #     # self.tweet_number += 1
    #       urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', tweet_info["text"])
    #       for each in urls:
    #         try:
    #           r = requests.get(each)
    #           tweet_info["text"] = tweet_info["text"].replace(each, r.url)
    #         except:
    #           continue
    #       csv_writer.writerow(tweet_info)

    #       if "arXiv" in tweet_info["text"]:
    #         return True
    #     return False
    # except:
    #   return False


keywords = get_keywords()

def match_GS_with_Twitter(file_name, output_file, GS_image_folder):
    with open(output_file, 'w') as csv_write:
        # csv_reader = csv.reader(csv_file)
        import numpy as np
        meta_GS_info = np.load(file_name, allow_pickle=True)
        csv_writer = csv.writer(csv_write)
        for row in meta_GS_info:
            real_name = row['name']
            if "/" in real_name:
                continue
            # print(real_name)
            # search_result = twitter.users.search(q = real_name)
            with jsonlines.open("./saved_user_info/" + real_name + ".jsonl", 'r') as reader:
                found_match = False
                for each_candidate in reader:
                    # if search_result:
                    #   index = 0
                    # for each_candidate in search_result:

                    # if index < 5:
                    candidate_screen_name = each_candidate["screen_name"]
                    # print("candidate_screen_name: ")
                    # print(candidate_screen_name)
                    # print('\n')
                    # try:
                    #     candidate_homepage_link = each_candidate['entities']['url']['urls'][0]['expanded_url']
                    #     # print("candidate_homepage_link: ")
                    #     # print(candidate_homepage_link)
                    #     # print('\n')
                    # except KeyError:
                    #     candidate_homepage_link = None
                    # homelink matched
                    # print("GS homelink is:" + row[4])
                    # if row[4] and candidate_homepage_link:
                    #     if match_by_homepage_link(candidate_homepage_link, row[4]):
                    #         csv_writer.writerow([real_name, candidate_screen_name, "match by homepage_link"])
                    #         found_match = True
                            # print("found by homelink\n")
                    # if the user has GS pictures, then compare two pictures
                    # img1 = "./" + GS_image_folder + '/' + real_name + ".jpg"
                    # if os.path.exists(img1):
                    #     img_link = each_candidate["profile_image_url"]
                    #     downloaded = download_profile_image(real_name, img_link)
                    #     if downloaded:
                    #         img2 = "./temp_pictures/" + real_name + ".jpg"
                    #         # same_image = whether_same_image(img1, img2)
                    #         # # print("downloaded")
                    #         # # no matter what is in the img, account match if profile photo is the same
                    #         # if same_image:
                    #         #   csv_writer.writerow([real_name, candidate_screen_name, "match by same image"])
                    #         #   found_match = True
                    #         #   # print("found by same image\n")
                    #         #   os.remove("./temp_pictures/" + real_name + '.jpg')
                    #         #   break
                    #
                    #         # compare human face in the img
                    #         same_person = compare_two_images(img1, img2)
                    #         if same_person:
                    #             csv_writer.writerow([real_name, candidate_screen_name, "match by same person in image"])
                    #             found_match = True
                    #             # print("found by same person\n")
                    #             os.remove("./temp_pictures/" + real_name + '.jpg')
                    #         os.remove("./temp_pictures/" + real_name + '.jpg')
                    #     # image not matched or no image
                    Twitter_discription = each_candidate["description"]
                    if each_candidate["entities"]["description"]["urls"]:
                        description_link = each_candidate["entities"]["description"]["urls"][0]["display_url"]
                        Twitter_discription = re.sub(
                            r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
                            description_link, Twitter_discription)
                    GS_meta_info = row['extra_info'][0]
                    # for i in row['extra_info']:
                    #     GS_meta_info += i
                    # print("meta descriptions are: ")
                    # print(Twitter_discription)
                    # print(GS_meta_info)
                    similiar_description = match_by_meta_description(Twitter_discription, GS_meta_info)
                    # ic(Twitter_discription, GS_meta_info)
                    # ic(similiar_description)
                    if similiar_description:
                        csv_writer.writerow([real_name, candidate_screen_name, "match by meta description"])
                        found_match = True
                        # print("found by description\n")
                    if if_keyword_match(Twitter_discription, keywords):
                        csv_writer.writerow([real_name, candidate_screen_name, "match by keywords in meta description"])
                        found_match = True
                    # matched_by_arXiv = match_by_tweets_arXiv(candidate_screen_name)
                    # if matched_by_arXiv:
                    #     csv_writer.writerow([real_name, candidate_screen_name, "match by twitter content"])
                    #     found_match = True
                    # index += 1
                if not found_match:
                    csv_writer.writerow([real_name, 'Not Found'])

            # should be delete, just to test the first person

def match_single_author(GS_info, twiteer_meta_info):
    # return a Boolean, whether it can be matched
    # found_match = False
    candidate_screen_name = twiteer_meta_info["screen_name"]
    twitter_discription = twiteer_meta_info["description"]
    if twiteer_meta_info["entities"]["description"]["urls"]:
        description_link = twiteer_meta_info["entities"]["description"]["urls"][0]["display_url"]
        twitter_discription = re.sub(
            r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
            description_link, twitter_discription)
    personal_webpage = GS_info.get("personal_webpage")
    try:
        candidate_homepage_link = twiteer_meta_info['entities']['url']['urls'][0]['expanded_url']
    except KeyError:
        candidate_homepage_link = None
    if personal_webpage and candidate_homepage_link:
        for i in personal_webpage:
            if match_by_homepage_link(candidate_homepage_link, i):
                return 1
    GS_meta_info = ""
    for i in GS_info['extra_info']:
        GS_meta_info+=i
    similiar_description = match_by_meta_description(twitter_discription, GS_meta_info)
    if if_keyword_match(twitter_discription, keywords):
        return 2
    if similiar_description:
        return 3
    return 0

if __name__ == '__main__':
    import numpy as np
    meta_GS_info = np.load("./data_from_GS/sample_info.npy", allow_pickle=True)
    ans = 0
    sum = 0
    for row in meta_GS_info:
        real_name = row['name']
        with jsonlines.open("./saved_user_info/" + real_name + ".jsonl", 'r') as reader:
            found_match = False
            for each_candidate in reader:
                if match_single_author(row, each_candidate):
                    ans+=1
        sum += 1
    print(ans)
    print(sum)


