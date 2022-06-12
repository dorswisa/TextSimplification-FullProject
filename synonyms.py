

import json
import requests
import csv
import re


from bs4 import BeautifulSoup
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import collections
import scipy as sp


# Hebrew Academy API

# text = 'צפן'
# url = "https://kalanit.hebrew-academy.org.il/api/Ac/?SearchString=" + text
# response = requests.get(url=url)
# json_response = response.json()
# print(json_response)

# Avenion API

# text = 'מביט'
# response = requests.get(url="https://www.milononline.net/do_search.php?sDIN=&Q=" + text)
# soup = BeautifulSoup(response.content, "html.parser")
# mydivs = soup.find_all("div", {"class": "result_box"})
# id = mydivs[0].select("div")[0].get("id").split("_")[1]
# url = "https://www.milononline.net/nirdaf.php?vldid="+id
# response = requests.get(url=url)
# by = list(response.content)
# by = list(map(lambda x: hex(x), by))
# by = [x if len(x) == 4 else x+"0" for x in by]
# by = [x[2:] for x in by]
# by = ''.join(by)
# code = bytes.fromhex(by).decode("windows-1255")
# soup = BeautifulSoup(code, "html.parser")
# alist = soup.find("span").findAll('a', style=False)
# nirdafot = [nirdaf.text.strip() for nirdaf in alist][:-1]
# print(nirdafot)


# Milog

text = 'התבונן'
response = requests.get(url="https://milog.co.il/" + text)
soup = BeautifulSoup(response.content, "html.parser")
mydiv = soup.find("div", {"class": "sr_e"})
href = mydiv.select("div")[0].select("a")[0].get("href")
response = requests.get(url=href)
soup = BeautifulSoup(response.content, "html.parser")
mydiv = soup.find("div", {"class": "ent_bar mm_opt_p2_selected"})
word = soup.find("div", {"class": "entry_title_text"}).getText()
word = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', word)                   # remove vowels
nirdafot = mydiv.parent.next_sibling.find("div", {"class": "ent_para_text"}).getText().split(",")
nirdafot = [nirdaf.strip() for nirdaf in nirdafot]
nirdafot = list(filter(lambda ele: " " not in ele, nirdafot))
print(nirdafot)
if word == text:
    # prediction for each word
    print(nirdafot)         # retrun the lowest score in prediction
if mydiv is not None:
    netiot = soup.select_one('span:-soup-contains("נטיות")').parent.find_all('a')
    netia = list(filter(lambda ele: text == re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', ele.getText()),netiot))[0].get("title")            # find netia
    response = requests.get(url="https://milog.co.il/" + nirdafot[-1])
    soup = BeautifulSoup(response.content, "html.parser")
    mydiv = soup.find_all("div", {"class": "sr_e"})
    mydiv = list(filter(lambda ele: ele.find("span") is not None and "גוף שלישי" in ele.find("span").getText(), mydiv))[0]
    href = mydiv.select("div")[0].select("a")[0].get("href")
    response = requests.get(url=href)
    soup = BeautifulSoup(response.content, "html.parser")
    netiot = soup.select_one('span:-soup-contains("נטיות")').parent.find_all('a')
    nirdaf = list(filter(lambda ele: netia == ele.get("title"), netiot))          # find nirdafot
    if nirdaf:
        print(nirdaf[0].getText())













