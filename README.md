# twitter_metainfo_scratch

## Code Structure
* `Counter(final_dict["matched_type"]): Counter({2: 678659, 1: 387688, 3: 59855})
`
* `Counter(matched): Counter({2: 10252, 1: 5363, 3: 950})`

## Description

The current code and the data is on the folder /cluster/project/sachan/zhiheng/twiteer at Euler server, because of the security reason, I save the twitter key as this structure, and use get_auth.py to load the key in the file. If you need more APIs, please contact me.

The current algorithm has the follow steps:

**Step1**: Find all twitter’s screen name by simply search the GS_name on twitter save_twitter_metainfo.py.
The problem now is that simply search the GS_name have a low recall rate, which is seen as the current bottleneck, about 52% of valid user loose in this step (see the below information)

**Step2**: Use match_and_save.py to make a sketch match by the type 1, 2, 3 match and save those users tweets
- type 1: matched by personal website
- type 2: matched by keyword
- type3: matched by similar description with the information in GS

**Step3**: Process the tweets (not important in current step). For the current 400 datapoint, there are 136 valid twitter accounts. I can match 20 of them by personal website, 36 of them by using type 1,2,3 match(with FN=20), and only 66 of them appeared in our search by users name (for example, if I simply search "Mohammad Moradi", I can not find the correspondent user moradideli by https://twitter.com/search?q=Mohammad%20Moradi&src=typed_query&f=user).

Here is some useful info about how a person annotator find the ground truth twitter user:

I followed the instruction in this doc by searching the name + Twitter in the Google first, and click top results to see if there is any match. If none, I will go search the name in Twitter and also browse through the top results. Sometimes I will also search their LinkedIn page to get their most up-to-date information. (the current institute in Google Scholar is not as accurate as their LinkedIn, and LinkedIn has a full history of where they worked. Moreover, they tend to put their photos in LinkedIn)

[https://drive.google.com/file/d/1fggQ21_61h_8el7LCryMQEj-qixg31S1/view?usp=sharing](https://drive.google.com/file/d/1fggQ21_61h_8el7LCryMQEj-qixg31S1/view?usp=sharing)
