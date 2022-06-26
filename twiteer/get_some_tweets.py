import jsonlines
num = 0
with jsonlines.open("/cluster/project/sachan/zhiheng/twiteer/final_output/tweets_data_news.jsonl", 'r') as reader:
    for i in reader:
        for j in i["tweets"]:
            with jsonlines.open("/cluster/project/sachan/zhiheng/twiteer/tweets.jsonl", 'a') as writer:
                writer.write(j)
                num += 1
            if (num == 20000):
                exit(0)