import requests
import csv
import json
import re
from bs4 import BeautifulSoup
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import collections
import scipy as sp

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

def syn(word) :
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


words = set()

index = 0

firstFile = open('StringFreqCorpus_M1.csv', 'r', newline='', encoding='UTF8')
writefile = open('78000-80000.csv','w',newline='',encoding='UTF8')
writer = csv.writer(writefile)
writer.writerow(["WORD","LOG-FREQ", "LENGTH", "SYLLABLES","POS", "COMPLEX"])
firstReader = csv.reader(firstFile)
for firstCSVEle in firstReader:
    if index < 78000:
        index = index + 1
        continue
    if index > 80000:
        break
    index = index + 1
    word = firstCSVEle[0]
    localhost_yap = "http://34.76.106.188:8000/yap/heb/joint"
    data = '{{"text": "{}  "}}'.format(word).encode('utf-8')  # input string ends with two space characters
    headers = {'content-type': 'application/json'}
    response = requests.get(url=localhost_yap, data=data, headers=headers)

    matrix = json.loads(response.text)['ma_lattice'].split('\n')
    matrix = list(filter(None, matrix))
    for el in matrix:
        row = el.split('\t')
        if len(row[2]) > 1:
            before = len(words)
            words.add((row[2], row[4]))
            after = len(words)
            if after > before:
                headers = {'Content-Type': 'text/plain;charset=utf-8'}
                params = {
                    "task": "nakdan",
                    "genre": "modern",
                    "data": row[2],
                    "addmorph": True,
                    "matchpartial": True,
                    "keepmetagim": False,
                    "keepqq": False,
                }
                r = requests.post("https://nakdan-4-0.loadbalancer.dicta.org.il/addnikud", headers=headers, json=params)
                r.encoding = "UTF-8"
                print(index)
                writer.writerow([row[2], firstCSVEle[2], len(row[2]), syn(json.loads(r.text)[0]['options'][0]['w']), row[4], firstCSVEle[3]])



