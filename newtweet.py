import tweepy
import telegram
import json
import datetime
import time
import pymongo
from mongoHandler import MongoHandler
from config import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
telegram_bot = telegram.Bot(token=telegram_bot_token)

maxLikes = None
maxRetweets = None


mongo = MongoHandler(mongo_connString, mongo_db, mongo_collection)
LastTweetToCheck = datetime.datetime.utcnow() - datetime.timedelta(seconds=checkTweetsWithin)
findQuery = {"retweeted_status.created_at": {'$gte': LastTweetToCheck}, "retweeted_status.retweeted": {'$ne': True}}
finderCursor = mongo._collection.find(findQuery).sort('retweeted_status.favorite_count', pymongo.DESCENDING)
for tweet in finderCursor:
    if maxLikes is None:
        maxLikes = tweet.copy()
        break

finderCursor = mongo._collection.find(findQuery).sort('retweeted_status.retweet_count', pymongo.DESCENDING)
for tweet in finderCursor:
    if maxRetweets is None:
        maxRetweets = tweet.copy()
        break

# print(maxLikes)

# mongo._collection.delete_one({'retweeted_status.id_str': maxLikes['retweeted_status']['id_str']})
# mongo._collection.delete_one({'retweeted_status.id_str': maxRetweets['retweeted_status']['id_str']})
maxLikes['retweeted_status']['retweeted'] = True
maxRetweets['retweeted_status']['retweeted'] = True
mongo._collection.update_many({"retweeted_status.id_str": maxLikes['retweeted_status']['id_str']},
                              {'$set': {'retweeted_status.retweeted': True}})
mongo._collection.update_many({"retweeted_status.id_str": maxRetweets['retweeted_status']['id_str']},
                              {'$set': {'retweeted_status.retweeted': True}})

if maxLikes['retweeted_status']['id_str'] == maxRetweets['retweeted_status']['id_str']:
    maxLikesAndRetweetsText = u'این توییت از @' + maxLikes['retweeted_status']['user']['screen_name'] + u' بیشترین لایک و ریتوییت در 3ساعت گذشته را داشته!\n'
    maxLikesAndRetweetsText += 'https://twitter.com/' + maxLikes['retweeted_status']['user']['screen_name'] + '/status/' + maxLikes['retweeted_status']['id_str']

    api.update_status(maxLikesAndRetweetsText)
    api.retweet(maxLikes['retweeted_status']['id_str'])
    telegram_bot.sendMessage(chat_id="@trenditter", text=maxLikesAndRetweetsText)
else:
    maxLikesText = u'این توییت از @' + maxLikes['retweeted_status']['user']['screen_name'] + u' با ' + str(maxLikes['retweeted_status']['favorite_count'])  + ' لایک بیشترین لایک رو در ۳ساعت اخیر داشته!\n'
    maxLikesText += 'https://twitter.com/' + maxLikes['retweeted_status']['user']['screen_name'] + '/status/' + maxLikes['retweeted_status']['id_str']

    maxRetweetsText = u'این توییت از @' + maxRetweets['retweeted_status']['user']['screen_name'] + u' با ' + str(maxRetweets['retweeted_status']['retweet_count']) +  u' ریتوییت بیشترین ریتوییت رو در ۳ساعت اخیر داشته!\n'
    maxRetweetsText += 'https://twitter.com/' + maxRetweets['retweeted_status']['user']['screen_name'] + '/status/' + maxRetweets['retweeted_status']['id_str']

    api.update_status(maxLikesText)
    api.retweet(maxLikes['retweeted_status']['id_str'])
    telegram_bot.sendMessage(chat_id="@trenditter", text=maxLikesText)

    print('maxLikesText tweeted!')

    api.update_status(maxRetweetsText)
    api.retweet(maxRetweets['retweeted_status']['id_str'])
    telegram_bot.sendMessage(chat_id="@trenditter", text=maxRetweetsText)

    print('maxRetweetsText tweeted!')


print("likes:")
print(maxLikes['retweeted_status']['favorite_count'])

print("retweets:")
print(maxRetweets['retweeted_status']['retweet_count'])
