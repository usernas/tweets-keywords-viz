"""
I will use Twitter API to listen for tweets containing a single keyword given by the user and
then extract more keywords that frequently appear in these tweets.
 And i will finally visualize these datas on webpage as a point cloud or using js animation.
"""

#UTILISATION DE SCIKIT LEARN POUR L'ALGO TFIDF
#https://stackoverflow.com/questions/12118720/python-tf-idf-cosine-to-find-document-similarity/18914884#18914884
#https://medium.freecodecamp.org/how-to-process-textual-data-using-tf-idf-in-python-cd2bbc0a94a3

#http://kavita-ganesan.com/extracting-keywords-from-text-tfidf/

#from sklearn.feature_extraction.text import CountVectorizer
import tweepy
import pandas as pd
import numpy as np
import re
import json
import webbrowser, os
from api_credentials import *
from config import *
from datetime import *
import argparse
import matplotlib

matplotlib.use('Agg')
'''
mpl.use('Agg')
mpl.rcParams['figure.figsize'] = (8,6)
mpl.rcParams['font.size'] = 12'''
# override tweepy.StreamListener to add logic to on_status


class MyStreamListener(tweepy.StreamListener):

    """classe permettant de réaliser un traitement sur les tweets reçus (stockage,
    analyse...)"""

    def __init__(self, nbTweetsLimit=5, stf="./datas/stored_tweets.json",index = "./viz/index.html"):
        self.keyword = ''
        self.timestamp = ''
        self.nb_tweets_limit = nbTweetsLimit
        self.cpt_tweets = 1
        self.stored_tweets_path = stf
        self.index_viz_path = index
        self.hist_path = "./viz/img/hist.png"
        self.max_value_hist = 10
        self.tweets_DataFrame = pd.DataFrame(
            columns=['author', 'text', 'timestamp'])
        #self.tweets_DataFrame_clean = {}

    def on_connect(self):
        print("Connexion établie")

    def on_data(self, data):
        try:
            with open("./tweets.json",'a') as file:
                json.dump(data,file)
            if(self.cpt_tweets <= self.nb_tweets_limit and not json.loads(data)['text'].startswith("RT @")):
                print("Tweet numéro ", self.cpt_tweets)
                #file = open(self.stored_tweets_path, 'a')

                self.tweets_DataFrame = self.tweets_DataFrame.append({
                    'author': json.loads(data)['user']['name'],
                    'text': json.loads(data)['text'],
                    'timestamp': json.loads(data)['created_at']}, ignore_index=True)

                self.cpt_tweets += 1

                #file.close()
                return True

            elif(json.loads(data)['text'].startswith("RT @") and self.cpt_tweets <= self.nb_tweets_limit):
                print("skip RT\n")
                return True

            else:

                print("Number of tweets exceded")
                #print(self.tweets_DataFrame.dtypes)
                #print(self.tweets_DataFrame)
                
                pd.set_option('display.max_colwidth', -1)

                tweetsTable = self.tweets_DataFrame.copy()
                #tweetsWordsDico = {}

                # DATA CLEANING
                
                #Exclusion du mot clé de l'utilisateur
                print("******************* EXCLUSION DU MOT CLE CHOISI *******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub("([^\w]*"+self.keyword+"[^\w]*)+|[|\\^&\r\n]+", ' ', x))
                
                # Minuscule
                print("******************* FORCER MINUSCULES *******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].str.lower()

                #Exclusion mentions
                print("******************* EXCLUSION MENTIONS *******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub("(\s*@[\w_-]+)",' ',x))

                #Suppression urls
                print("******************* EXCLUSION URLS *******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub("(?P<url>https?:\/\/[^\s]+)",' ',x ))

                # Suppression des caractères spéciaux avec une regex
                print("******************* SUPPRESSION DES CARACTERES SPECIAUX *******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub('[\W]+', ' ', x))
                
                # Suppression des digits
                print("******************* SUPPRESSION DES DIGITS *******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub("[\d]+", ' ', x))
                
                #création liste de mots
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: x.split())

                #exclusion des mots appartenant à la stoplist
                rows1 = list()
                newRow = list()

                #préciser encodage sinon stoplist récupère \ufeff
                with open("./datas/stop_words.txt", 'r',encoding='utf-8-sig') as stoplist:
                    stopwords = set(stopword.strip('\n') for stopword in stoplist)
                    for i,t in self.tweets_DataFrame.iterrows():
                        end_tweets_cpt = 0
                        if newRow!=[]:
                            print(newRow)
                            rows1[i-1][1] = newRow[:]
                            rows1[i-1] = tuple(rows1[i-1])
                            newRow[:] = []
                        rows1.append([t['author'],list(),t['timestamp']])
                        for word in t['text']:
                            end_tweets_cpt+=1
                            if(word not in stopwords):
                                print("Ajouté au tweet")
                                newRow.append(word)
                            if(end_tweets_cpt == len(t['text']) and i == len(self.tweets_DataFrame)-1):
                                print("FIN DU DATAFRAME")
                                rows1[i] = (t['author'],newRow[:],t['timestamp'])

                self.tweets_DataFrame = pd.DataFrame(rows1,columns=['author','text','timestamp'])
 
                #ALGO TF-IDF
                #Création d'un second dataframe regroupant tous les mots par document
                    #https://sigdelta.com/blog/text-analysis-in-pandas/
                    #http://kavita-ganesan.com/extracting-keywords-from-text-tfidf/#.XNcAUbvVKUk
                rows2 = list()
                cpt_docs = 0
                
                #création d'un autre dataframe regroupant document/mot (id_document | mot)
                for row in self.tweets_DataFrame[['text']].iterrows():
                    cpt_docs += 1
                    r = row[1]
                    for word in r.text:
                        rows2.append((cpt_docs,word))
                words = pd.DataFrame(rows2,columns=['id tweet','word']) 

                #modification dataframe ajout du nombre d'apparition associé à un mot dans un document (id_document | mot | nb d'appararition dans le document)
                counts = words.groupby('id tweet').word.value_counts().to_frame().rename(columns={'word':'word_occurence_tweet'})

                #création d'un histogramme des x mots les plus fréquents dans le corpus
                ax = counts.count(level="word").sort_values(by="word_occurence_tweet", ascending = False)[0:self.max_value_hist].plot.bar()
                fig = ax.get_figure()
                fig.savefig(self.hist_path, bbox_inches='tight')


                #on récupère ensuite le nombre de mots total de chaque tweet permettant de calculer le tf
                word_sum = counts.groupby(level=0).sum().rename(columns={'word_occurence_tweet':'nb_words_tweets'})

                #on joint ensuite les 2 colonnes pour ainsi calculer le tf
                tf = counts.join(word_sum)
                tf['tf'] = tf.word_occurence_tweet/tf.nb_words_tweets

                print(tf)
                #export page html
                with open(self.index_viz_path, 'w') as file:
                    file.write(htmlContent.format(
                    	motCle = self.keyword,
                    	nbTweets = self.nb_tweets_limit,
                    	timestamp= self.timestamp,
                    	hist = "../"+self.hist_path,
                    	wordcloud = 'Wordcloud',
                    	table = tweetsTable.to_html(table_id="tweetsTable")
                    	))              

                
                return False

        except BaseException as e:
            print("Error : ", str(e))
            return True

    def on_error(self, status_code):
        print(status_code)

if __name__ == "__main__":

    timestamp = str(datetime.now())

    auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    MyStreamListener = MyStreamListener()

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('keyword', help="Le mot clé à rechercher")
    parser.add_argument('nbMaxTweets', type = int ,help="Le nombre de tweets maximum à récupérer")
    parser.add_argument('indexPath',help="Le chemin vers la page html de visualisation à générer")

    args = parser.parse_args()

    MyStreamListener.keyword = str(args.keyword)
    MyStreamListener.nb_tweets_limit = int(args.nbMaxTweets)
    MyStreamListener.index_viz_path = str(args.indexPath)

    MyStreamListener.timestamp = timestamp
    
    f = open(MyStreamListener.stored_tweets_path, "w")
    f.close()
    myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener, tweet_mode='extended')
    myStream.filter(languages=["fr"],track=[str(' '+MyStreamListener.keyword+' ')])
