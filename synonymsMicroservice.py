from flask import Flask, request, abort, jsonify
from flask import json,Response
from flask_cors import CORS, cross_origin
import json
import requests
import csv
import re

import fasttext
import fasttext.util
import numpy as np

from bs4 import BeautifulSoup
import networkx as nx
import pandas as pd
import collections
import scipy as sp

from keras.models import load_model
from sklearn import preprocessing

model = load_model('200epc,128batch_model.h5')                                                     # load model

df = pd.read_csv('vectorsDataset.csv')

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

dataset = df.values

X = dataset[:, 0:304]

min_max_scaler = preprocessing.MinMaxScaler()
scaler = min_max_scaler.fit(X)

REMOVAL_RANGES = [
    '/[\u0591-\u05AF]/g',
    '/[\u05BD-\u05C7]/g']

lettersByName = {
    'alef': '\u05D0',
    'bet': '\u05D1',
    'gimel': '\u05D2',
    'dalet': '\u05D3',

    'he': '\u05D4',
    'vav': '\u05D5',
    'zayin': '\u05D6',

    'het': '\u05D7',
    'tet': '\u05D8',
    'yod': '\u05D9',

    'kaf': '\u05DB',
    'lamed': '\u05DC',
    'mem': '\u05DE',
    'nun': '\u05E0',

    'samekh': '\u05E1',
    'ayin': '\u05E2',
    'pe': '\u05E4',
    'tsadi': '\u05E6',

    'qof': '\u05E7',
    'resh': '\u05E8',
    'shin': '\u05E9',
    'tav': '\u05EA',

    'finalKaf': '\u05DA',
    'finalMem': '\u05DD',
    'finalNun': '\u05DF',
    'finalPe': '\u05E3',
    'finalTsadi': '\u05E5'
};

vowelsByName = {
    'patah': '\u05B7',
    'qamats': '\u05B8',
    'tsere': '\u05B5',
    'hiriq': '\u05B4',
    'shuruqDagesh': '\u05BC',

    'segol': '\u05B6',
    'holamHaser': '\u05BA',

    'holam': '\u05B9',
    'qubuts': '\u05BB',
    'sheva': '\u05B0',
    'hatafSegol': '\u05B1',
    'hatafPatah': '\u05B2',
    'hatafQamats': '\u05B3'
};

def dec2hex(textString) :
    return format(int(textString), 'x')

def convertCharString(textString, parameters, pad, type) :
    haut = 0
    n = 0
    CPstring = ''
    afterEscape = False
    for i in textString:
        b = i.encode('utf-16')
        if haut != 0 :
            if 0xdc00 <= b and b <= 0xdfff :
                if afterEscape :
                    CPstring += ' '
                if type == 'hex' :
                    CPstring += dec2hex(0x10000 + ((haut - 0xd800) << 10) + (b - 0xdc00))
                else :
                    CPstring += 0x10000 + ((haut - 0xd800) << 10) + (b - 0xdc00)
                haut = 0
                continue
            else :
                haut = 0

        if 0xd800 <= b and b <= 0xdbff:
            haut = b
        else:
            if afterEscape:
                    CPstring += ' '
            if type == 'hex':
                cp = dec2hex(b);
                if pad:
                    while cp.length < 4 :
                        cp = '0'+ cp
                else:
                    cp = b
                CPstring += cp
                afterEscape = True
    return CPstring


def convertUnicode(string):
    return convertCharString(string, 'none', 4, 'hex')

def isLetter(string = ''):
    return string in list(lettersByName.values())

def mapVowels(word = '') :
    results = [];
    vowelBuilder = '';
    letterBuilder = {};

    for char in word:
        if isLetter(char):
            if 'letter' not in letterBuilder.keys():
                letterBuilder['letter'] = char
            else:
                if len(vowelBuilder) > 0:
                    letterBuilder['vowels'] = vowelBuilder
                else:
                    letterBuilder['vowels'] = None
                results.append(letterBuilder)
                vowelBuilder = ''

                if word[-1] == char :
                    letterBuilder = { 'letter': char, 'vowels': None };
                    results.append(letterBuilder)
                    vowelBuilder = ''
                else :
                    letterBuilder = { 'letter': char }
        else :
            if word[-1] == char :
                vowelBuilder += char
                letterBuilder['vowels'] = vowelBuilder
                results.append(letterBuilder)
                vowelBuilder = ''
            else :
                vowelBuilder += char
    return results

def isShevaCounted(word = [], letterPairIndex = 0) :
    if letterPairIndex == 0:
        return True

    if vowelsByName['shuruqDagesh'] in word[letterPairIndex]['vowels']:
        return True

    if letterPairIndex + 1 < len(word):
        if word[letterPairIndex]['letter'] == word[letterPairIndex + 1]['letter'] and word[letterPairIndex + 1]['vowels'] is None:
            return True

    if letterPairIndex != len(word) - 1 and word[letterPairIndex + 1]['vowels'] is not None and vowelsByName['sheva'] in word[letterPairIndex + 1]['vowels'] and letterPairIndex + 1 != len(word) - 1 :
        return True

    return False

def syl(word) :
    totalSyllableCount = 0
    word = mapVowels(word)
    for letterPairIndex, letterPair in enumerate(word):
        if letterPair['vowels'] != None :
            if vowelsByName['sheva'] in letterPair['vowels']:
                if isShevaCounted(word, letterPairIndex):
                    totalSyllableCount = totalSyllableCount + 1
            else :
                if vowelsByName['shuruqDagesh'] == letterPair['vowels']:
                    if lettersByName['vav'] in letterPair['letter']:
                        totalSyllableCount = totalSyllableCount + 1
                else:
                    totalSyllableCount = totalSyllableCount + 1
    return totalSyllableCount


ft = fasttext.load_model('cc.he.300.bin')

POS = ["ABVERB","AT","BN","BNN","CC","CD","CDT","CONJ","COP","COP_TOINFINITIVE","DEF","DT","DTT","DUMMY_AT","EX","IN","INTJ","JJ","JJT","MD","NN","NN_S_PP","NNP","NNT","P","POS","PREPOSITION","PRP","QW","S_PRN","TEMP","VB","VB_TOINFINITIVE","yyCLN","yyCM","yyDASH","yyDOT","yyELPS","yyEXCL","yyLRB","yyQM","yyQUOT","yyRRB","yySCLN","RB","NEG","BNT","TTL","NNPT"]

microservice = Flask(__name__)
cors = CORS(microservice)

@microservice.route('/cwi', methods=['GET'])
def cwi():
    text = request.args.get('text')
    localhost_yap = "http://localhost:8000/yap/heb/joint"
    data = '{{"text": "{}  "}}'.format(text).encode('utf-8')  # input string ends with two space characters
    headers = {'content-type': 'application/json'}
    response = requests.get(url=localhost_yap, data=data, headers=headers)
    matrix = json.loads(response.text)['md_lattice'].split('\n')
    matrix = list(filter(None, matrix))
    headers = {'Content-Type': 'text/plain;charset=utf-8'}
    params = {
        "task": "nakdan",
         "genre": "modern",
         "data": text,
         "addmorph": True,
         "matchpartial": True,
         "keepmetagim": False,
         "keepqq": False,
    }
    r = requests.post("https://nakdan-4-0.loadbalancer.dicta.org.il/addnikud", headers=headers, json=params)
    print(json.loads(response.text)['ma_lattice'])
    print(json.loads(response.text)['md_lattice'])
    print(json.loads(response.text)['dep_tree'])
    dicta = json.loads(r.text)
    words = []
    del dicta[1::2]

    for id, ele in enumerate(matrix):
        matrix[id] = ele.split('\t')

    for id, el in enumerate(dicta):
        obj = {}
        pos = [value for value in matrix if value[-1] == str(id+1)][-1][4]
        nikud = el['options'][0]['w'].split("|")[1] if '|' in el['options'][0]['w'] else el['options'][0]['w']
        word = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', nikud)
        format = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', el['options'][0]['w'])
        features = np.array([10, len(word), syl(nikud), POS.index(pos)])
        wordVec = ft.get_word_vector(word)
        fullWordVec = np.append(wordVec, features, 0)
        scaleFullWordVec = scaler.transform(fullWordVec.reshape(1, -1))
        cmpx = model.predict(scaleFullWordVec[0:1])
        obj["word"] = word
        obj["format"] = format
        obj["nikud"] = nikud
        obj["pos"] = pos
        obj["features"] = features.tolist()
        obj["complex"] = True if cmpx > 0.5 else False
        obj["change"] = False
        words.append(obj)
        print(obj)

    json_string = json.dumps(words, ensure_ascii=False)
    # creating a Response object to set the content type and the encoding
    response = Response(json_string, content_type="application/json; charset=utf-8")
    return response

@microservice.route('/synonym', methods=['GET'])
def synonym():
    word = request.args.get('word')
    pos = word.split("-")[1]
    word = word.split("-")[0]
    nirdafot = None

    response = requests.get(url="https://milog.co.il/" + word)
    soup = BeautifulSoup(response.content, "html.parser")
    sr_e = soup.find_all("div", {"class": "sr_e"})
    if len(sr_e) == 0:
        return "None"
    if pos == "VB" or pos == "BN":
        mydiv = list(filter(lambda ele: ele.find("span") is not None and "גוף שלישי" in ele.find("span").getText(), sr_e))
        print(mydiv)
        if len(mydiv) > 0:
            mydiv = mydiv[0]
        else:
            mydiv = list(filter(lambda ele: ele.find("span") is not None, sr_e))
            if len(mydiv) > 0:
                mydiv = mydiv[0]
            else:
                mydiv = sr_e[0]
    else:
        mydiv = list(filter(lambda ele: ele.find("span") is not None, sr_e))
        if len(mydiv) > 0:
            mydiv = mydiv[0]
        else:
            mydiv = sr_e[0]

    href = mydiv.select("div")[0].select("a")[0].get("href")
    response = requests.get(url=href)
    soup = BeautifulSoup(response.content, "html.parser")
    mydiv = soup.find("div", {"class": "ent_bar mm_opt_p2_selected"})
    if mydiv:
        milogword = soup.find("div", {"class": "entry_title_text"}).getText()
        milogword = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', milogword)  # remove vowels
        nirdafot = mydiv.parent.next_sibling.find("div", {"class": "ent_para_text"}).getText().split(",")
        nirdafot = [nirdaf.strip() for nirdaf in nirdafot]
        nirdafot = list(filter(lambda ele: " " not in ele, nirdafot))
    rating = []
    if nirdafot:
        for el in nirdafot:
            localhost_yap = "http://localhost:8000/yap/heb/joint"
            data = '{{"text": "{}  "}}'.format(re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', el)).encode('utf-8')  # input string ends with two space characters
            headers = {'content-type': 'application/json'}
            response = requests.get(url=localhost_yap, data=data, headers=headers)
            matrix = json.loads(response.text)['ma_lattice'].split('\n')
            matrix = list(filter(None, matrix))
            headers = {'Content-Type': 'text/plain;charset=utf-8'}
            params = {
                "task": "nakdan",
                "genre": "modern",
                "data": re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', el),
                "addmorph": True,
                "matchpartial": True,
                "keepmetagim": False,
                "keepqq": False,
            }
            r = requests.post("https://nakdan-4-0.loadbalancer.dicta.org.il/addnikud", headers=headers, json=params)
            dicta = json.loads(r.text)
            for id, ele in enumerate(matrix):
                matrix[id] = ele.split('\t')

            wordele = [value for value in matrix if value[3] == re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', el) and value[4] == pos]
            if len(wordele) > 0:
                wordele = wordele[0]
                newpos = wordele[4]
            else:
                wordele = [value for value in matrix if value[3] == re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', el)]
                if len(wordele) > 0:
                    wordele = wordele[0]
                    newpos = wordele[4]
                else:
                    newpos = pos
            nikud = dicta[0]['options'][0]['lex'] if '|' in dicta[0]['options'][0]['w'] else dicta[0]['options'][0]['w']
            print(nikud)
            wrd = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', nikud)
            features = np.array([10, len(wrd), syl(nikud), POS.index(newpos)])
            wordVec = ft.get_word_vector(wrd)
            fullWordVec = np.append(wordVec, features, 0)
            scaleFullWordVec = scaler.transform(fullWordVec.reshape(1, -1))
            cmpx = model.predict(scaleFullWordVec[0:1])
            rating.append(cmpx)

        index = rating.index(min(rating))
        low = nirdafot[index]

        if word == milogword:
            return re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', low)
        if mydiv is not None:
            netiot = soup.select_one('span:-soup-contains("נטיות")').parent.find_all('a')
            netia = list(filter(lambda ele: word == re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', ele.getText()),netiot))[0].get("title")  # find netia
            response = requests.get(url="https://milog.co.il/" + low)
            soup = BeautifulSoup(response.content, "html.parser")
            sr_e = soup.find_all("div", {"class": "sr_e"})
            if pos == "VB" or pos == "BN":
                mydiv = list(filter(lambda ele: ele.find("span") is not None and "גוף שלישי" in ele.find("span").getText(), sr_e))
                if len(mydiv) > 0:
                    mydiv = mydiv[0]
                else:
                    mydiv = list(filter(lambda ele: ele.find("span") is not None, sr_e))
                    if len(mydiv) > 0:
                        mydiv = mydiv[0]
                    else:
                        return "None"
            else:
                mydiv = list(filter(lambda ele: ele.find("span") is not None, sr_e))
                if len(mydiv) > 0:
                    mydiv = mydiv[0]
                else:
                    return "None"
            href = mydiv.select("div")[0].select("a")[0].get("href")
            response = requests.get(url=href)
            soup = BeautifulSoup(response.content, "html.parser")
            netiot = soup.select_one('span:-soup-contains("נטיות")').parent.find_all('a')
            nirdaf = list(filter(lambda ele: netia == ele.get("title"), netiot))  # find nirdafot
            print(nirdaf)
            if nirdaf:
                return re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', nirdaf[0].getText())
    return "None"

if __name__ == '__main__':
    microservice.run(debug=True, port=3005)