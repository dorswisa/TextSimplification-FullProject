import json
import requests
import csv
import re


from bs4 import BeautifulSoup
import networkx as nx
import pandas as pd
import collections
import scipy as sp
import fasttext
import fasttext.util
import numpy as np
ft = fasttext.load_model('cc.he.300.bin')
print()

POS = ["ABVERB","AT","BN","BNN","CC","CD","CDT","CONJ","COP","COP_TOINFINITIVE","DEF","DT","DTT","DUMMY_AT","EX","IN","INTJ","JJ","JJT","MD","NN","NN_S_PP","NNP","NNT","P","POS","PREPOSITION","PRP","QW","S_PRN","TEMP","VB","VB_TOINFINITIVE","yyCLN","yyCM","yyDASH","yyDOT","yyELPS","yyEXCL","yyLRB","yyQM","yyQUOT","yyRRB","yySCLN","RB","NEG","BNT","TTL","NNPT"]

index = 0

firstFile = open('finalDataset.csv', 'r', newline='')
writefile = open('vectorsDataset.csv','w',newline='',encoding='UTF8')
writer = csv.writer(writefile)
firstReader = csv.reader(firstFile)
for firstCSVEle in firstReader:
    if index < 1:
        index = index + 1
        continue

    index = index + 1
    word = firstCSVEle[0]

    wordVec = ft.get_word_vector(word)
    features = np.array([firstCSVEle[1], firstCSVEle[2], firstCSVEle[3], POS.index(firstCSVEle[4]), firstCSVEle[5]])
    row = np.append(wordVec, features, 0)
    print(index)
    writer.writerow(row)
