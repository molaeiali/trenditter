import tweepy
import telegram
import json
import datetime
import time
import pymongo
from mongoHandler import MongoHandler
from config import *
import re
import traceback

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
telegram_bot = telegram.Bot(token=telegram_bot_token)

def persianNumbersAndLetters(str):
    str = str.replace('1','۱')
    str = str.replace('2','۲')
    str = str.replace('3','۳')
    str = str.replace('4','۴')
    str = str.replace('5','۵')
    str = str.replace('6','۶')
    str = str.replace('7','۷')
    str = str.replace('8','۸')
    str = str.replace('9','۹')
    str = str.replace('0','۰')
    str = str.replace('ك','ک')
    str = str.replace('ي','ی')
    return str

def sendToTelegram(tweet, desc=""):
    text = ''
    pre = ' '.join(re.sub("(@[A-Za-z0-9_]+)|(?:\@|https?\://)\S+"," ",tweet['retweeted_status']['text']).split())

    text += tweet['retweeted_status']['user']['name'] + u":\n"
    text += persianNumbersAndLetters(re.sub("_", "ـ", pre)) + '\n\n'

    text += persianNumbersAndLetters(desc) + '\n\n'

    text += u'[لینک به توییت](' + 'https://twitter.com/' + tweet['retweeted_status']['user']['screen_name'] + '/status/' + tweet['retweeted_status']['id_str'] + u')'

    text += u'\n[@' + tweet['retweeted_status']['user']['screen_name'] + u']'
    text += u'(https://twitter.com/' + tweet['retweeted_status']['user']['screen_name'] + u')'


    ret = telegram_bot.sendMessage(chat_id="@trenditter", text=text, parse_mode=telegram.ParseMode.MARKDOWN)

    return ret



maxLikes = None
maxRetweets = None


mongo = MongoHandler(mongo_connString, mongo_db, mongo_collection)
LastTweetToCheck = datetime.datetime.utcnow() - datetime.timedelta(seconds=checkTweetsWithin)
findQuery = {"retweeted_status.created_at": {'$gte': LastTweetToCheck}, "retweeted_status.retweeted": {'$ne': True}}
finderCursor = mongo._collection.find(findQuery).sort('retweeted_status.favorite_count', pymongo.DESCENDING)
for tweet in finderCursor:
    realStatus = api.get_status(tweet['retweeted_status']['id_str'])
    if realStatus.retweeted:
        continue
    if maxLikes is None:
        maxLikes = tweet.copy()
#        maxLikes['retweeted_status']['favorite_count'] = realStatus.retweeted_status.favorite_count
        break

finderCursor = mongo._collection.find(findQuery).sort('retweeted_status.retweet_count', pymongo.DESCENDING)
for tweet in finderCursor:
    realStatus = api.get_status(tweet['retweeted_status']['id_str'])
    if realStatus.retweeted:
        continue
    if maxRetweets is None:
        maxRetweets = tweet.copy()
#        maxRetweets['retweeted_status']['retweet_count'] = realStatus.retweeted_status.retweet_count
        break

try:
    if maxLikes['retweeted_status']['id_str'] == maxRetweets['retweeted_status']['id_str']:
        desc = u'این توییت با ' + str(maxLikes['retweeted_status']['favorite_count'])
        desc += u' لایک و ' + str(maxLikes['retweeted_status']['retweet_count']) + u' ریتوییت '
        desc += u'بیشترین لایک و ریتوییت ۱ساعت گذشته را داشته! ✌️🤘🏻\n\n'

        api.retweet(maxLikes['retweeted_status']['id_str'])
        mongo._collection.update_many({"retweeted_status.id_str": maxLikes['retweeted_status']['id_str']},
                                      {'$set': {'retweeted_status.retweeted': True}})
        sendToTelegram(maxLikes, desc)
        telegram_bot.sendMessage(chat_id=admin_id, text="لایک‌ها و ریتوییت‌ها ریتوییت شد :)")
    else:
        likesDesc = u'این توییت با ' + str(maxLikes['retweeted_status']['favorite_count'])
        likesDesc += u' لایک '
        likesDesc += u'بیشترین لایک ۱ساعت گذشته را داشته! ✌️🤘🏻\n\n'

        api.retweet(maxLikes['retweeted_status']['id_str'])
        mongo._collection.update_many({"retweeted_status.id_str": maxLikes['retweeted_status']['id_str']},
                                      {'$set': {'retweeted_status.retweeted': True}})
        maxLikesTG = sendToTelegram(maxLikes, likesDesc)

        print('maxLikesText tweeted!')
        telegram_bot.forwardMessage(chat_id=admin_id, from_chat_id="@trenditter", message_id=maxLikesTG.message_id)

        retweetsDesc = u'این توییت با '
        retweetsDesc += str(maxRetweets['retweeted_status']['retweet_count']) + u' ریتوییت '
        retweetsDesc += u'بیشترین ریتوییت ۱ساعت گذشته را داشته! ✌️🤘🏻\n\n'

        api.retweet(maxRetweets['retweeted_status']['id_str'])
        mongo._collection.update_many({"retweeted_status.id_str": maxRetweets['retweeted_status']['id_str']},
                                      {'$set': {'retweeted_status.retweeted': True}})
        maxRtTG = sendToTelegram(maxRetweets, retweetsDesc)

        print('maxRetweetsText tweeted!')
        telegram_bot.forwardMessage(chat_id=admin_id, from_chat_id="@trenditter", message_id=maxRtTG.message_id)

except Exception as e:
    telegram_bot.sendMessage(chat_id=admin_id, text="الان مشکلی پیش‌اومده!")
    telegram_bot.sendMessage(chat_id=admin_id, text=str(traceback.format_exc()))
    telegram_bot.sendMessage(chat_id=admin_id, text=str(maxLikes['_id']))
    telegram_bot.sendMessage(chat_id=admin_id, text=str(maxRetweets['_id']))


print("likes:")
print(maxLikes['retweeted_status']['favorite_count'])

print("retweets:")
print(maxRetweets['retweeted_status']['retweet_count'])
