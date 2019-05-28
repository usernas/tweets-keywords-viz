"""
I will use Twitter API to listen for tweets containing a single keyword given by the user and
then extract more keywords that frequently appear in these tweets.
 And i will finally visualize these datas on webpage as a point cloud or using js animation.
"""



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
import math
from PIL import Image
from wordcloud import WordCloud

matplotlib.use('Agg')


class MyStreamListener(tweepy.StreamListener):

    """classe permettant de réaliser un traitement sur les tweets reçus (stockage,
    analyse...)"""

    def __init__(self, nbTweetsLimit,index = "./viz/index.html"):
        self.keyword = ''
        self.timestamp = ''
        self.nb_tweets_limit = nbTweetsLimit
        self.cpt_tweets = 1
        self.index_viz_path = index
        self.hist_path = "./viz/img/hist.png"
        self.wordcloud_path = "./viz/img/wordcloud.png"
        self.max_value_hist = 25
        self.max_words_cloud = 100
        self.max_displayed_tweets = int(math.ceil(self.nb_tweets_limit*0.05))
        self.tweets_DataFrame = pd.DataFrame(
            columns=['author', 'text', 'timestamp'])

    def on_connect(self):
        print("Connexion établie")

    def on_data(self, data):
        try:
            if(self.cpt_tweets <= self.nb_tweets_limit and not json.loads(data)['text'].startswith("RT @")):
                print("Tweet numéro ", self.cpt_tweets)

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
                
                pd.set_option('display.max_colwidth', -1)

                tweetsTable = self.tweets_DataFrame.copy()

                # DATA CLEANING
                
                #Exclusion du mot clé de l'utilisateur
                print("******************* EXCLUSION DU MOT CLE CHOISI *******************")
                self.tweets_DataFrame['text'] = self.tweets_DataFrame['text'].apply(lambda x: re.sub("([^\w]*#*"+self.keyword+"[^\w]*)+|[|\\^&\r\n]+", ' ', x))
                
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
                            rows1[i-1][1] = newRow[:]
                            rows1[i-1] = tuple(rows1[i-1])
                            newRow[:] = []
                        rows1.append([t['author'],list(),t['timestamp']])
                        for word in t['text']:
                            end_tweets_cpt+=1
                            if(word not in stopwords):
                                newRow.append(word)
                            if(end_tweets_cpt == len(t['text']) and i == len(self.tweets_DataFrame)-1):
                                rows1[i] = (t['author'],newRow[:],t['timestamp'])

                self.tweets_DataFrame = pd.DataFrame(rows1,columns=['author','text','timestamp'])
 
                #ALGO TF-IDF
                #Création d'un second dataframe regroupant tous les mots par document
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
                fig.savefig(self.hist_path, bbox_inches='tight', dpi=160)


                #on récupère ensuite le nombre de mots total de chaque tweet permettant de calculer le tf
                word_sum = counts.groupby(level=0).sum().rename(columns={'word_occurence_tweet':'nb_words_tweets'})

                #on joint ensuite les 2 colonnes pour ainsi calculer le tf
                tf = counts.join(word_sum)
                tf['tf'] = tf.word_occurence_tweet/tf.nb_words_tweets

                #on récupère ensuite la fréquence d'apparition de chaque mots dans le corpus (mot | nb de document dans lequel il apparaît)
                idf = words.groupby('word')['id tweet'].nunique().to_frame().rename(columns={'id tweet':'word_occurence_corpus'})

                #on calcule ensuite l'idf de chaque mot selon la formule
                idf['idf'] = np.log(words['id tweet'].nunique()/idf.word_occurence_corpus.values)
                
                #on joint ensuite les 2 dataframes et on calcule le tf_idf en multipliant chaque valeur du mot associé                
                tf_idf = tf.join(idf)

                tf_idf['tf_idf'] = tf_idf.tf * tf_idf.idf

                #on crée ensuite un dataframe propre contenant seulement les 3 colonnes importantes:
                #(id tweet | mot) | indice tf_idf associé
                tf_idf_clean = tf_idf['tf_idf'].to_frame()
                
                #on transforme ensuite celui-ci en dictionnaire et on crée un second dataframe contenant
                #les tweets et leur valeur tf_idf associé
                rows3 = list()
                finalWordDict = {}
                for i in tf_idf_clean.iterrows():
                    rows3.append((i[0][0], i[1][0]))
                    finalWordDict[i[0][1]] = i[1][0]
                tweets_Weight = pd.DataFrame(rows3, columns=['id_tweet','tf_idf'])                
                tweet_Weight = tweets_Weight.groupby('id_tweet').sum().sort_values('tf_idf',ascending = False)
                
                #on crée un set d'id des tweets les plus significatifs
                listIdTweets = set()
                cpt = 1
                for i,row in tweet_Weight.iterrows():
                    if(cpt<=self.max_displayed_tweets):
                        listIdTweets.add(i)
                    cpt+=1

                #on récupère ces tweets dans le dataframe original
                listDisplayedTweets = list()
                for i,row in tweetsTable.iterrows():
                    if(i in listIdTweets):
                        listDisplayedTweets.append(row)

                dfDisplayedTweets = pd.DataFrame(listDisplayedTweets)
                dfDisplayedTweets.columns=['Auteur', 'Tweet','Date et heure']
                
                #on génère pour finir l'image du nuage de mot à inclure dans la page web       
                cloud = WordCloud(background_color="black",width=800,height=800, max_words=self.max_words_cloud,relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(finalWordDict)
                cloud.to_file(self.wordcloud_path)
                
                #export en page html
                with open(self.index_viz_path, 'w') as file:
                    file.write(htmlContent.format(
                    	motCle = self.keyword,
                    	nbTweets = self.nb_tweets_limit,
                    	timestamp= self.timestamp,
                    	hist = "../"+self.hist_path,
                    	wordcloud = '../'+self.wordcloud_path,
                    	table = dfDisplayedTweets.to_html(table_id="tweetsTable", index=False)
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

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('keyword', help="Le mot clé à rechercher")
    parser.add_argument('nbMaxTweets', type = int ,help="Le nombre de tweets maximum à récupérer")

    args = parser.parse_args()
    
    MyStreamListener = MyStreamListener(int(args.nbMaxTweets))

    MyStreamListener.keyword = str(args.keyword) 

    MyStreamListener.timestamp = timestamp
    
    myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener, tweet_mode='extended')
    myStream.filter(languages=["fr"],track=[str(' '+MyStreamListener.keyword+' ')])
