from os import path
from PIL import Image
import numpy as np
import datetime
import pymongo
from mongoHandler import MongoHandler
from config import *
from persian_wordcloud.wordcloud import STOPWORDS, PersianWordCloud
import arabic_reshaper
from bidi.algorithm import get_display

d = path.dirname(__file__)

# convert rtl words like Arabic and Farsi to some showable form
def convert(text):
    new_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(new_text)
    return bidi_text

def is_perisan(s):
        return u'\u0600' <= s <= u'\u06FF'

mongo = MongoHandler(mongo_connString, mongo_db, mongo_collection)
LastTweetToCheck = datetime.datetime.utcnow() - datetime.timedelta(seconds=wordCloudTimeout)
findQuery = {"retweeted_status.created_at": {'$gte': LastTweetToCheck}}
finderCursor = mongo._collection.find(findQuery)
print(finderCursor.count())

all_words = []
# Read the whole text.
for tweet in finderCursor:
    txt = tweet['retweeted_status']['text'].split()
    txt_formated = u""
    for word in txt:
        if is_perisan(word):
            words = ''
            words += ' ' + word
            all_words.append(words)

text = ''.join(all_words)
print("finished")

# generating stopwords
stopwords = set(STOPWORDS)
stopwords_list = open(path.join(d, 'blacklist.txt')).read()
for word in stopwords_list.split():
    stopwords.add(convert(word))
    stopwords.add(word)

# loading the mask
twitter_mask = np.array(Image.open(path.join(d, "twitter_mask.png")))

# generating wordcloud
wc = PersianWordCloud(only_persian=True, font_path=path.join(d, "IRANSans.ttf"), background_color="white", max_words=1500, mask=twitter_mask,
            stopwords=stopwords)
wc.generate(text)


currTime = datetime.datetime.utcnow()
output_name = currTime.strftime("%d-%m-%Y_%H_%M.png")
#output_name = "test.png"

# store to file
wc.to_file(path.join(d, output_name))


import tweepy
import telegram
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
telegram_bot = telegram.Bot(token=telegram_bot_token)

api.update_with_media(path.join(d, output_name), u'توییتر به روایت تصویر :))))))')
telegram_bot.send_photo(chat_id="@trenditter", photo=open(path.join(d, output_name), 'rb'), caption=u'توییتر به روایت تصویر :)')
