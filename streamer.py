import tweepy
import json
import datetime
import time
from mongoHandler import MongoHandler
from config import *
from os import path

d = path.dirname(__file__)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):

    _mongo = MongoHandler(mongo_connString, mongo_db, mongo_collection)
    _blacklist = open(path.join(d, 'users_blacklist.txt')).read().split()

    def on_data(self, data):
        tweet = json.loads(data)
        if 'retweeted_status' in tweet:
            #tweet_cnt = self._mongo._collection.find({"retweeted_status.id_str": tweet['retweeted_status']['id_str']}).count()
            #if tweet_cnt:
            #    self._mongo._collection.update_many({"retweeted_status.id_str": tweet['retweeted_status']['id_str']},
            #                                        {'$set': {"retweeted_status.favorite_count": tweet['retweeted_status']['favorite_count']}})
            #    self._mongo._collection.update_many({"retweeted_status.id_str": tweet['retweeted_status']['id_str']},
            #                                        {'$set': {"retweeted_status.retweet_count": tweet['retweeted_status']['retweet_count']}})
            #    return True
            tcreated = datetime.datetime.strptime(tweet['retweeted_status']['created_at'], '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=None)
            if tcreated - datetime.datetime.utcnow() <= datetime.timedelta(seconds=60 * 60 * 24):
                tweet['retweeted_status']['created_at'] = tcreated
                if u'ة' not in tweet['retweeted_status']['text'] and u'أ' not in tweet['retweeted_status']['text'] and not tweet['retweeted_status']['retweeted'] and tweet['retweeted_status']['user']['screen_name'] not in self._blacklist:
                    self._mongo.insert(tweet)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    listener = StdOutListener()

    print("streaming all new tweets for persian language!")

    # There are different kinds of streams: public stream, user stream,
    #    multi-user streams
    # In this example follow #programming tag
    # For more details refer to https://dev.twitter.com/docs/streaming-apis
    stream = tweepy.Stream(auth, listener)
    stream.filter(track=[u'با', u'هر', u'از', u'و', u'من',
                  u'تا', u'به', u'را', u'رو', u'که'],
                  languages=['fa'])
