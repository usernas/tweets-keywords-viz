"""
I will use Twitter API to listen for tweets containing a single keyword given by the user and
then extract more keywords that frequenbTweetsLimity appears in these tweets.
 And i will finally visualize these datas on webpage as a point cloud or using js animation.
"""

#UTILISATION DE SCIKIT LEARN POUR L'ALGO TFIDF
#https://stackoverflow.com/questions/12118720/python-tf-idf-cosine-to-find-document-similarity/18914884#18914884
#https://medium.freecodecamp.org/how-to-process-textual-data-using-tf-idf-in-python-cd2bbc0a94a3

#http://kavita-ganesan.com/extracting-keywords-from-text-tfidf/

import tweepy
import pandas as pd
import numpy as np
import re
import json
import webbrowser, os
from api_credentials import *
from config import *
from datetime import *

# override tweepy.StreamListener to add logic to on_status


class MyStreamListener(tweepy.StreamListener):

    """classe permettant de réaliser un traitement sur les tweets reçus (stockage,
    analyse...)"""

    def __init__(self, nbTweetsLimit=5, stf="datas/stored_tweets.json"):
        self.keyword = ''
        self.timestamp = ''
        self.nb_tweets_limit = nbTweetsLimit
        self.cpt_tweets = 1
        self.stored_tweets_file = stf
        self.tweets_DataFrame = pd.DataFrame(
            columns=['author', 'text', 'timestamp'])
        #self.tweets_DataFrame_clean = {}

    def on_connect(self):
        print("Connexion établie")

    def on_data(self, data):
        try:
            if(self.cpt_tweets <= self.nb_tweets_limit and not json.loads(data)['text'].startswith("RT @")):
                print("Tweet numéro ", self.cpt_tweets)
                file = open(self.stored_tweets_file, 'a')

                self.tweets_DataFrame = self.tweets_DataFrame.append({
                    'author': json.loads(data)['user']['name'],
                    'text': json.loads(data)['text'],
                    'timestamp': json.loads(data)['created_at']}, ignore_index=True)

                self.cpt_tweets += 1

                file.close()
                return True

            elif(json.loads(data)['text'].startswith("RT @") and self.cpt_tweets <= self.nb_tweets_limit):
                print("skip RT\n")
                return True

            else:

                print("Number of tweets exceded")
                # print(self.tweets_DataFrame.dtypes)
                print(self.tweets_DataFrame)
                
                pd.set_option('display.max_colwidth', -1)
                


                # Data cleaning
#Exclure stop list et mot clé
                # Minuscule
                print("*******************FORCER MINUSCULES*******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].str.lower()

                # Suppression des caractères spéciaux avec une regex
                print("*******************SUPPRESSION DES CARACTERES SPECIAUX*******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub('[\W]+', ' ', x))
                
                # Suppression des digits
                print("*******************SUPPRESSION DES DIGITS*******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub("[\d]+", ' ', x))

                print("*******************EXCLUSION DU MOT CLE CHOISI*******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub(keyword, ' ', x))
                
                print(self.tweets_DataFrame)
                #stockage dans un fichier
                #self.tweets_DataFrame.to_html("./viz/index.html", table_id="tweetsList")
                with open('./viz/index.html', 'w') as file:
                    file.write(htmlContent.format(
                    	motCle = self.keyword,
                    	nbTweets = self.nb_tweets_limit,
                    	timestamp= self.timestamp,
                    	hist = 'Histogramme',
                    	table=self.tweets_DataFrame.to_html(table_id="tweetsTable")
                    	))
                return False

        except BaseException as e:
            print("Error : ", str(e))
            return True

    def on_error(self, status_code):
        print(status_code)

if __name__ == "__main__":

    timestamp = str(datetime.now())
    keyword = input("Entrez le mot-clé à tracker : ")
    keyword = str(keyword)

    auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    MyStreamListener = MyStreamListener()
    MyStreamListener.keyword = keyword
    MyStreamListener.timestamp = timestamp
    f = open(MyStreamListener.stored_tweets_file, "w")
    f.close()
    myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener)
    myStream.filter(languages=["fr"],track=[MyStreamListener.keyword])
