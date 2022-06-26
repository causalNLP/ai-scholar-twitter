import json
import tweepy
import requests
import re
import time

def get_auth(file_path):
    with open(file_path,'r') as load_file:
        auth_dict=json.load(load_file)
        # print(auth_dict)
    consumer_key = auth_dict.get("API_key");
    consumer_secret = auth_dict.get("API_secret_key")
    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    return auth

class API_controler:
    def __init__(self):
        self.apis = []
        self.current_api = 0

    def add_api(self, api):
        self.apis.append(api)

    def change_api(self):
        self.current_api += 1
        if (self.current_api>=len(self.apis)):
            self.current_api = 0
        return self.apis[self.current_api]



if __name__ == "__main__":
    print(get_auth("./auth_1.json"))