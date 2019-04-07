"""
I will use Twitter API to listen for tweets containing a single keyword given by the user and
then extract more keywords that frequently appears in these tweets.
 And i will finally visualize these datas on webpage as a point cloud or using js animation.
"""
import tweepy
import pandas as pd
import numpy as np
import re
import json
from api_credentials import *

# override tweepy.StreamListener to add logic to on_status


class MyStreamListener(tweepy.StreamListener):

    """classe permettant de réaliser un traitement sur les tweets reçus (stockage,
    analyse...)"""

    def __init__(self, ntl=5, stf="datas/stored_tweets.json"):
        self.nb_tweets_limit = ntl
        self.cpt_tweets = 1
        self.stored_tweets_file = stf
        self.tweets_DataFrame = pd.DataFrame(
            columns=['author', 'text', 'timestamp'])

    def on_connect(self):
        print("Connexion établie")

    def on_data(self, data):
        try:
            if(self.cpt_tweets <= self.nb_tweets_limit and not json.loads(data)['text'].startswith("RT @")):
                print("Tweet numéro ", self.cpt_tweets)
                file = open(self.stored_tweets_file, 'a')
                # file.write(data)
                # print(json.loads(data)['user']['screen_name'])
                # print(json.loads(data)['text'],"\n")
                self.tweets_DataFrame = self.tweets_DataFrame.append({
                    'author': json.loads(data)['user']['name'],
                    'text': json.loads(data)['text'],
                    'timestamp': json.loads(data)['created_at']}, ignore_index=True)
                self.cpt_tweets += 1
                file.close()
                return True

            elif(json.loads(data)['text'].startswith("RT @")):
                print("skip RT\n")
                return True

            else:
                print("Number of tweets exceded")
                # print(self.tweets_DataFrame.dtypes)
                print(self.tweets_DataFrame)
                # Data cleaning
                # Minuscule
                print("*******************FORCER MINUSCULES*******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].str.lower()
                print(self.tweets_DataFrame)

                # Suppression des caractères spéciaux avec une regex
                print("*******************SUPPRESSION DES CARACTERES SPECIAUX*******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub('[\W]+', ' ', x))
                print(self.tweets_DataFrame)                
                # Suppression des digits
                print("*******************SUPPRESSION DES DIGITS*******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub('[\d]+', ' ', x))

                print(self.tweets_DataFrame)

                self.tweets_DataFrame.to_csv(self.stored_tweets_file,sep='\t|\t')
                return False

        except BaseException as e:
            print("Error : ", str(e))
            return True

    def on_error(self, status_code):
        print(status_code)

if __name__ == "__main__":

    keyword = input("Entrez le mot-clé à tracker : ")
    keyword = str(keyword)

    auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    MyStreamListener = MyStreamListener()
    f = open(MyStreamListener.stored_tweets_file, "w")
    f.close()
    myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener)
    myStream.filter(languages=["fr"],track=[keyword])
