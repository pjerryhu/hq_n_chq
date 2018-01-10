#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import threading
import os
import time
import crayons
import nltk
import pytesseract
from googleapiclient.discovery import build
from PIL import Image, ImageEnhance
import unicodedata
import re
import subprocess
import urllib
# from urllib.parse   import quote
# from urllib.request import urlopen


SCREEN_DIR = "/Users/pengxianghu/Desktop/Screenshots" 
IDENTIFIER = "Screen Shot"
DEBUG = False

STUB = [{'snippet': ""}, {'snippet': ""}]
MY_API_KEY = "AIzaSyBv7qDkBUXiysQQqsPcgXCcFB9svNeTl4k"
MY_CSE_ID = "012086291608697037198:z2impkka__g"

# api to search through google custom api
def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

# approach 2: general search on question prompt
def app2Search(search_term,options, result_counts):
    global MY_API_KEY, MY_CSE_ID
    res = google_search(search_term, MY_API_KEY, MY_CSE_ID, num=10)
    results = res['items'] if 'items' in res else STUB
    records = map(lambda result: result['snippet'], results)
    queryRes = " ".join(records).lower()
    for option in options:
        result_counts[option] = queryRes.count(option.lower()) 

# approach 3: number of search results on question prompt
def app3Search(question, option, scopes):
    global MY_API_KEY, MY_CSE_ID
    res = google_search(
            question+' "'+option+'"', \
            MY_API_KEY, MY_CSE_ID, num=10)
    scopes[option] = int(res['searchInformation']['formattedTotalResults'].replace(",",""))


# overall search handler
def search(question, options):

    # vanilla google search 
    # vanilla google search 
    url = "https://www.google.com.tr/search?q="+question
    subprocess.call(["open", url])
    # url = u''.join([url, question]).encode('utf-8')
    # print url
    # webbrowser.open(url)

    result_counts = {}
    app2 = threading.Thread(target=app2Search, args=(question,options,result_counts))
    app2.start()

    scopes = {}
    popScores = {}

    app3ops = {}
    for option in options:
        app3ops[option] = threading.Thread(target=app3Search, args=(question,option,scopes))
        app3ops[option].start()
        
    app2.join()
    for option in options:
        app3ops[option].join()

    return {'count':result_counts,'scope': scopes}

def process_image(img):
    width, height = img.size
    # shorter ones is at height * 52
    img = img.crop((width*0.1, height*0.2, width*0.90, height * 0.60))

    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(3)
    

    sharper = ImageEnhance.Sharpness(img)
    img = sharper.enhance(2)

    brighter = ImageEnhance.Brightness(img)
    img = brighter.enhance(2)

    img = img.convert("L")
    threshold = 150
    img = img.point(lambda p: p > threshold and 255)

    return img

def run_solver(screen_shot):
    os.system("clear")

    if IDENTIFIER not in screen_shot:
        print(crayons.yellow("No screen shot found"))
        return

    # this is to let the system to respond and revert the file 
    # screen shot file format from .Screen...XXX to Screen Shot
    time.sleep(0.1)
    start = screen_shot.index('Screen Shot')
    end = screen_shot.index('png')
    screen_shot = screen_shot[start:end+3]

    # step 1: image pre-processing and OCR recognition
    file_path = os.path.join(SCREEN_DIR, screen_shot)
    screen = process_image(Image.open(file_path))
    screen.save(SCREEN_DIR + "/test.png")
    result = pytesseract.image_to_string(screen, lang='chi_sim')

    # step 2: Parse up the question and answer options
    parts = result.split("\n\n")
    ind = map(lambda word:"?" in word, parts).index(True)
    question = " ".join(parts[:ind+1]).replace("\n", " ")
    question = question[question.index(".")+1:]
    options = parts[ind+1:]

    # step 3: do google search with 2 separate approaches
    answer_results = search(question, options)
    

    # step 4: printing the results
    print("\n{}\n\n{}\n\n".format(
        crayons.blue(question),
        crayons.blue(", ".join(options)),
    ))

    if sum(answer_results['count'].itervalues()) > 0:
        print(crayons.green("Good for 'what' type question\n"))
        for key,value in sorted(answer_results['count'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
            print(crayons.green(key +":"+ str(value)))

    if sum(answer_results['scope'].itervalues()) > 0:
        print(crayons.red("\nGood for 'which' or selection type question\n"))
        for key,value in sorted(answer_results['scope'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
            print(crayons.red(key +":"+ str(value)))

    if not DEBUG:
        os.rename(file_path, file_path.replace("Screen Shot", "Done"))
    
    
