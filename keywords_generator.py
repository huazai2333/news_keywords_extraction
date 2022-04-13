#MultiKeywordsEx接口调用示例
import requests
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def get_keywords(sour):
    sour.strip()
    url = 'https://eae266ec46b040f9afb1ae22bef2676e.apig.cn-north-4.huaweicloudapis.com/v1/infers/240dd325-dfaf-4950-81a1-992f3aae0164/api/MultiKeywordsEx'
    data = {"token": "test", "keywordsNumber": "6", "sourList": sourList}
    data = json.dumps(data)
    data = data.encode('UTF-8')
    headers = {'Content-Type': 'application/json',
               'X-Apig-AppCode': '2fbd1dee3ec64bf3a35c860027f00d84faa45118659841f3a28153759f78e2cc'}
    r = requests.post(url, data=data, headers=headers)
    tmp = r.json()
    return tmp['kewords'].split('；')[:-1]


def get_wordcloud(wordlist):
    w = WordCloud(background_color='white',
                  width=900,height=600,
                  max_words=100,
                  font_path='simhei.ttf',
                  max_font_size=99,
                  min_font_size=16,
                  random_state=42)

    w.generate_from_frequencies(wordlist)
    w.to_file('mywordcloud.png')
