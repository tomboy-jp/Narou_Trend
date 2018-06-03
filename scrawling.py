import re
import os
import pandas as pd
import requests
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

def get_data():

    df = pd.DataFrame(columns=['ncode', 'title', 'point', 'word_cnt', 'start_date', 'docs'])

    ncode_pattern = re.compile(r'ncode/.+')
    title_pattern = re.compile(r'<h1><a href="https://ncode.syosetu.com/.+?</a></h1>')
    point_pattern = re.compile(r'<td>[0-9,]+?pt</td>')
    word_cnt_pattern = re.compile(r'<td>[0-9,]+?文字</td>')
    start_date_pattern = re.compile(r'<td>[0-9,]+?年.+?分</td>')

    tmp_index = []
    index_cnt = 1

    while len(df) < 5000:

        sleep(3)

        index_url = "https://yomou.syosetu.com/search.php?&type=r&order=new&notnizi=1&p=" + str(index_cnt)

        try:

            index_html = requests.get(index_url, headers=headers)

        except:

            continue

        soup = BeautifulSoup(index_html.content, "lxml")
        tmp_index = [re.search(ncode_pattern, str(a.get("href"))).group(0)[6:-1] for a in soup.find_all("a") if re.search(ncode_pattern, str(a.get("href")))]

        index_cnt += 1

        for j in tmp_index:

            sleep(3)

            detail_url = "https://ncode.syosetu.com/novelview/infotop/ncode/" + j

            try:

                detail_html = requests.get(detail_url, headers=headers)


                detail_soup = BeautifulSoup(detail_html.content, "lxml")

                title = re.sub(r'<.+?>' , '', re.search(title_pattern ,str(detail_soup.find_all("h1"))).group(0))

                point = re.sub(r'<.+?>' , '', re.search(point_pattern ,str(detail_soup.find_all("tr"))).group(0))
                point = int(re.sub(r'pt', '', point).replace(',',''))

                word_cnt = re.sub(r'<.+?>' , '', re.search(word_cnt_pattern ,str(detail_soup.find_all("tr"))).group(0))
                word_cnt = int(re.sub(r'文字', '', word_cnt).replace(',',''))

                start_date = re.sub(r'<.+?>' , '', re.search(start_date_pattern ,str(detail_soup.find_all("tr"))).group(0))
                start_date = datetime(int(start_date[0:4]), int(start_date[6:8]), int(start_date[9:11]), int(start_date[13:15]), int(start_date[16:18]))


            except:

                continue

            if word_cnt >= 5000 and int(start_date.strftime("%Y%m%d")) > 20171231 and int(start_date.strftime("%Y%m%d")) < 20180501:

                page_cnt = 1
                docs = ""

                while len(docs) < 5000:

                    sleep(3)

                    novel_url = "https://ncode.syosetu.com/" + j + "/" + str(page_cnt)

                    try:

                        novel_html = requests.get(novel_url, headers=headers)

                        novel_soup = BeautifulSoup(novel_html.content, "lxml")
                        parsed = novel_soup.find_all("div", id ="novel_honbun")
                        parsed = re.sub(r'<.+?>', '', str(parsed[0]))
                        parsed = re.sub(r'(・)', '', parsed)
                        parsed = re.sub(r'\n', '', parsed)
                        parsed = re.sub(r'\u3000', '', parsed)

                        docs += parsed
                        page_cnt += 1

                    except:

                        break

                if len(docs) >= 5000:

                    se = pd.Series([j, title, point, word_cnt, start_date, docs], index=df.columns)
                    print(se)

                    df = df.append(se, ignore_index = True)

        df = df.duplicated().reset_index(drop=True)

    return df


def saving(df):

    try:

        os.mkdir("data")

    except:

        pass

    df.to_csv("data/data" + datetime.now().strftime("%Y%m%d") + ".csv")


if __name__ == "__main__":

    df = get_data()
    saving(df)
