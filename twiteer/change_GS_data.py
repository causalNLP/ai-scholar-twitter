import numpy as np
from bs4 import BeautifulSoup
import re

if __name__ == "__main__":
    #total_info = np.load("/cluster/project/sachan/zhiheng/datasets/GS_info/final_anser_cites100.npy", allow_pickle=True)
    total_info = np.load("/cluster/project/sachan/zhiheng/datasets/GS_info/78k_scholar_new.npy", allow_pickle=True)
    meta_info = [[],[],[],[]]
    for i in total_info:
        meta_info[0].append(i['name'])
        meta_info[1].append(i['url'].split("user=")[-1])
        text = ""
        urls = []
        for html in i['extra_info']:
            soup = BeautifulSoup(html, 'html.parser')
            for k in soup.find_all('a'):
                urls.append(k['href'])
            for subsection in html.split("<"):
                text += subsection.split(">")[-1] + ' '
        meta_info[2].append(text)
        meta_info[3].append(urls)


    print(meta_info[0][0:10])
    print(meta_info[1][0:10])
    print(meta_info[2][0:10])
    print(meta_info[3][0:10])
    a=np.array(meta_info)
    np.save("meta_info.npy", meta_info)

