import re
import os
import pandas as pd
from sys import exit
import requests
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

def get_index():

    df = pd.DataFrame(columns=['ncode', 'title', 'point', 'word_cnt', 'start_date', 'genre', 'docs'])

    ncode_pattern = re.compile(r'ncode/.+')
    title_pattern = re.compile(r'<h1><a href="https://ncode.syosetu.com/.+?</a></h1>')
    point_pattern = re.compile(r'<td>[0-9,]+?pt</td>')
    word_cnt_pattern = re.compile(r'<td>[0-9,]+?文字</td>')
    start_date_pattern = re.compile(r'<td>[0-9,]+?年.+?分</td>')

    tmp_index = []

    for i in range(1,3):

        sleep(3)

        index_url = "https://yomou.syosetu.com/search.php?&type=r&order=new&notnizi=1&p=" + str(i)
        index_html = requests.get(index_url, headers=headers)
        soup = BeautifulSoup(index_html.content, "lxml")
        tmp_index = [re.search(ncode_pattern, str(a.get("href"))).group(0)[6:-1] for a in soup.find_all("a") if re.search(ncode_pattern, str(a.get("href")))]

        for j in tmp_index:

            sleep(3)

            se = pd.Series(index=df.index)
            detail_url = "https://ncode.syosetu.com/novelview/infotop/ncode/" + j
            detail_html = requests.get(detail_url, headers=headers)
            detail_soup = BeautifulSoup(detail_html.content, "lxml")

            title = re.sub(r'<.+?>' , '', re.search(title_pattern ,str(detail_soup.find_all("h1"))).group(0))

            point = re.sub(r'<.+?>' , '', re.search(point_pattern ,str(detail_soup.find_all("tr"))).group(0))
            point = int(re.sub(r'pt', '', point).replace(',',''))

            word_cnt = re.sub(r'<.+?>' , '', re.search(word_cnt_pattern ,str(detail_soup.find_all("tr"))).group(0))
            word_cnt = int(re.sub(r'文字', '', word_cnt).replace(',',''))

            start_date = re.sub(r'<.+?>' , '', re.search(start_date_pattern ,str(detail_soup.find_all("tr"))).group(0))
            start_date = datetime(int(start_date[0:4]), int(start_date[6:8]), int(start_date[9:11]), int(start_date[13:15]), int(start_date[16:18]))

    print(start_date)

if __name__ == "__main__":

    get_index()
