"""
I will use Twitter API to listen for tweets containing a single keyword given by the user and
then extract more keywords that frequently appears in these tweets.
 And i will finally visualize these datas on webpage as a point cloud or using js animation.
"""
import tweepy
#import pandas
from api_credentials import *

# override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
    
    """classe permettant de réaliser un traitement sur les tweets reçus (stockage,
    analyse...)"""

    def __init__(self, ntl=10, stf="datas/stored_tweets.json"):
        self.nb_tweets_limit = ntl
        self.cpt_tweets = 1
        self.stored_tweets_file = stf

    def on_connect(self):
    	print("Connexion établie")

    def on_data(self, data):
        try:
            if(self.cpt_tweets <= self.nb_tweets_limit):
                print("Tweet numéro ", self.cpt_tweets)
                file = open(self.stored_tweets_file, 'a')
                file.write(data)
                # ou écrire dans un fichier ou stocker dans une dataframe
                self.cpt_tweets += 1
                file.close()
                return True
            else:
                print("Number of tweets exceded")
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
    myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener)
    myStream.filter(track=[keyword])
