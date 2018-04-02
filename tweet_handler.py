import requests
from bs4 import BeautifulSoup
import os.path
import re

def getTime(obj):
    return int(obj.find('span', {'class': '_timestamp'})['data-time'])


def getReadableTime(tweet):
    return tweet.find('a', {'class': 'tweet-timestamp js-permalink js-nav js-tooltip'})['title']


def getLastTime(user):
    dir = "log"
    file = os.path.join(dir, user)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if not os.path.isfile(file):
        with open(file, 'w') as f:
            f.write("0")
    with open(file) as f:
        lastKnownTime = int(f.read())
    return lastKnownTime


def writeTime(user, time):
    with open("log/%s" % user, "w") as f:
        f.write(str(time))


def getTweetData(tweet):
    return tweet.find('div', {'class': 'js-tweet-text-container'}).find('p').getText()


def isRetweet(tweet):
    if tweet.find('span', {'class': 'js-retweet-text'}):
        return True
    return False


def getTweets(user):
    data = BeautifulSoup(
        requests.get("https://twitter.com/i/profiles/show/%s/timeline/tweets" % (user)).json()['items_html'], 'lxml')

    allTweets = data.find_all('li', {'class': 'js-stream-item stream-item stream-item '})
    pinnedTweet = data.find('li', {'class': 'js-stream-item stream-item stream-item js-pinned '})

    tweets = []

    if pinnedTweet is not None:
        tweets.append([getTime(pinnedTweet), getReadableTime(pinnedTweet), getTweetData(pinnedTweet)])
    for tweet in allTweets:
        if not isRetweet(tweet):
            tweets.append([getTime(tweet), getReadableTime(tweet), getTweetData(tweet)])
    tweets.sort(key=lambda tweet1: tweet1[0], reverse=True)
    return tweets


def getNewTweets(user, latest=False):

    latestTweets = getTweets(user)
    if latest:
        print("Date: {}\nText: {} ".format(latestTweets[0][1], latestTweets[0][2]))
    lastTweetTime = getLastTime(user)
    if len(latestTweets) == 0:
        return None
    if lastTweetTime >= latestTweets[0][0]:
        return None
    newTweets = []
    writeTime(user, latestTweets[0][0])
    for tweet in latestTweets:
        if tweet[0] > lastTweetTime:
            newTweets.append(tweet)
        else:
            return newTweets
    return newTweets


if __name__ == "__main__":
    accounts = ['sudokoin']
    for acct in accounts:
        newTweets = getNewTweets(acct)
        if newTweets is not None:
            new_tweet = newTweets[0][2]
            date = newTweets[0][1]
            print("--NEW TWEET--: Date: {}\nText: {} ".format(date, new_tweet))
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                              new_tweet)[0]

        else:
            getNewTweets(acct, latest=True)
