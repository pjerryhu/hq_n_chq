# hq_n_chq

## Overview
This project is inspired by 
https://hackernoon.com/i-hacked-hq-trivia-but-heres-how-they-can-stop-me-68750ed16365 . Make sure you read it to understand the general idea.
I also referenced some ideas of this repo 
https://github.com/nbclark/hqcheat .

#### py-version/ is for english version
#### py-c-version/ is for chinese version

## Steps
1. Open quicktime
2. File->New Movie Recording
3. Choose your iphone and put the window somewhere convenient
4. Open terminal and "python handler.py"
5. cmd + shift + 4, then hit space bar to capture iphone screen recording when question shows up.
6. The terminal will watch new images on the desktop, run OCR and google answers
7. Choose the answer recommended (and/or) use your best judgement

## Trouble Shoot
1. make sure you change path (path='/Users/{your mac name}/Desktop/Screenshots') at https://github.com/phu02/hq_n_chq/blob/master/py-version/handler.py#L16 and some other places in solver.py
