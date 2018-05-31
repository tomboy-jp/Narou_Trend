import re
import os
from sys import exit
import requests
from time import sleep
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

def get_index():

    index_url = "https://yomou.syosetu.com/search.php?&type=r&order=new&notnizi=1&p="
    index = []
    pattern = re.compile(r'/ncode/.+')

    for i in range(1,3):

        sleep(1)

        index_html = requests.get(index_url + str(i), headers=headers)
        soup = BeautifulSoup(index_html.content, "lxml")
        index += [a.get("href") for a in soup.find_all("a") if re.search(pattern, str(a.get("href")))]


    print(index)

if __name__ == "__main__":

    get_index()
