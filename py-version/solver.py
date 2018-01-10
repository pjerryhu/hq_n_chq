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
import webbrowser

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# Regular expression for negation by Christopher Potts
NEGATION = set(['never','no','nothing','nowhere','none','not'
            ,"haven't","hasn't","hadn't","can't","couldn't","shouldn't"
            ,"won't","wouldn't","don't","doesn't","didn't","isn't","aren't", "ain't"])

SCREEN_DIR = "/Users/pengxianghu/Desktop/Screenshots" 
IDENTIFIER = "Screen Shot"
DEBUG = False

STUB = [{'snippet': ""}, {'snippet': ""}]
MY_API_KEY = "AIzaSyBv7qDkBUXiysQQqsPcgXCcFB9svNeTl4k"
MY_CSE_ID = "012086291608697037198:z2impkka__g"
STOPWORDS = set(nltk.corpus.stopwords.words("english"))

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
def app3Search(joined_q_terms, option, scopes):
    global MY_API_KEY, MY_CSE_ID
    res = google_search(
            joined_q_terms+' "'+option+'"', \
            MY_API_KEY, MY_CSE_ID, num=10)
    scopes[option] = int(res['searchInformation']['formattedTotalResults'].replace(",",""))


# approach 4: term frequency on option searched results
# step 1, run search on option,
# step 2, results.join on space.lower().split(" ").less stop words
# step 3, run term frequency to get the score
# step 4, normalize by the size of the return result
# step 5, give score
def tfSearch(q_terms, option, tfscores):
    global MY_API_KEY, MY_CSE_ID
    res = google_search(
            option, \
            MY_API_KEY, MY_CSE_ID, num=10)

    results = res['items'] if 'items' in res else STUB
    records = map(lambda result: result['snippet'], results)
    # pre-process terms
    temp_terms =  re.findall("\\w+", " ".join(records).lower())
    wordBank = filter(lambda word:word not in STOPWORDS and len(word) > 2, temp_terms)

    term_count = sum(map(lambda word: wordBank.count(word), q_terms))
    tc = term_count*1.0 / len(wordBank) if len(wordBank) != 0 else 0
    tcp = round(tc * 10000, 2)
    tfscores[option] = tcp


# overall search handler
def search(question, options, joined_q_terms):
    
    # vanilla google search 
    url = "https://www.google.com.tr/search?q="
    url = u''.join([url, question]).encode('utf-8')
    webbrowser.open(url)

    result_counts = {}
    app2 = threading.Thread(target=app2Search, args=(question,options,result_counts))

    scopes = {}
    tfscores = {}
    popScores = {}

    app3ops = {}
    tfops = {}
    for option in options:
        app3ops[option] = threading.Thread(target=app3Search, args=(joined_q_terms,option,scopes))
        tfops[option] = threading.Thread(target=tfSearch, args=(joined_q_terms.split(" "),option,tfscores))

    app2.start()
    for option in options:
        app3ops[option].start()
        tfops[option].start()

    app2.join()
    for option in options:
        app3ops[option].join()
        tfops[option].join()

    return {'count':result_counts,'scope': scopes, \
        'tfscore': tfscores}

def process_image(img):
    width, height = img.size
    img = img.crop((width*0.10, height*0.22, width*0.9, height * 0.65))

    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(2)

    sharper = ImageEnhance.Sharpness(img)
    img = sharper.enhance(2)

    img = img.convert("L")
    # threshold = 230
    # below two lines are good for pre-eliminated
    threshold = 110
    img = img.point(lambda p: p > threshold and 255)
    
    img.show()
    return img

def run_solver(screen_shot):
    os.system("clear")
    
    if IDENTIFIER not in screen_shot:
        print(crayons.yellow("No screen shot found"))
        return
    
    time.sleep(0.1)
    start = screen_shot.index("Screen Shot")
    end = screen_shot.index("png")
    screen_shot = screen_shot[start:end+3]

    # step 1: image pre-processing and OCR recognition
    file_path = os.path.join(SCREEN_DIR, screen_shot)
    # print file_path
    # print screen_shot
    screen = process_image(Image.open(file_path))
    # screen.save(SCREEN_DIR + "/test.png")

    result = pytesseract.image_to_string(
        screen, config="load_system_dawg=0 load_freq_dawg=0")
    result = unicodedata.normalize('NFKD', result)

    # step 2: Parse up the question and answer options
    parts = result.lower().split("\n\n")
    ind = map(lambda word:"?" in word, parts).index(True)
    question = " ".join(parts[:ind+1]).replace("\n", " ")
    options = parts[ind+1:]
    

    negation_flag = len(set(question.split(" ")).intersection(NEGATION)) > 0

    # query terms: question less stop words
    q_terms = filter(lambda t: t not in STOPWORDS and len(t) > 2, question.split(" "))
    joined_q_terms = " ".join(q_terms)
    # print joined_q_terms


    # step 3: do google search with 3 separate approaches
    answer_results = search(question, options, joined_q_terms)
    

    # step 4: printing the results
    print("\n{}\n\n{}\n\n".format(
        crayons.blue(question),
        crayons.blue(", ".join(options)),
    ))

    
    if sum(answer_results['count'].itervalues()) > 0:
        if 'what' in question:
            print color.BOLD + "Good for 'what' type question\n" + color.END
        else:
            print(crayons.green("Good for 'what' type question\n"))
        for key,value in sorted(answer_results['count'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
            print(crayons.green(key +":"+ str(value)))

    
    if sum(answer_results['scope'].itervalues()) > 0:
        if 'which' in question:
            print color.BOLD + "\nGood for 'which' or selection type question\n" + color.END
        else:
            print(crayons.red("\nGood for 'which' or selection type question\n"))
        for key,value in sorted(answer_results['scope'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
            print(crayons.red(key +":"+ str(value)))

    
    if sum(answer_results['tfscore'].itervalues()) > 0:
        print(crayons.yellow("\nTerm Frequency excluding question prompt search (cleared the celebrity effect)\n"))
        for key,value in sorted(answer_results['tfscore'].iteritems(), key=lambda (k,v): (v,k), reverse=True):
            print(crayons.yellow(key +":"+ str(value)))

    print(crayons.blue("\nNEGATION_FLAG" if negation_flag == 1 else ""))

    if not DEBUG:
        os.rename(file_path, file_path.replace("Screen Shot", "Done"))
    


    
