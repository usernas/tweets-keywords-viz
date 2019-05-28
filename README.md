# Tweets keyword viz

Ce script python permet de visualiser les mots les plus importants de tweets contenant un mot clé choisi par l'utilisateur. Une page web sera alors générée à l'exécution, permettant de révéler une tendance.
Cette page web contiendra alors :
* Un histogramme contenant les mots apparaissant le plus fréquemment dans le corpus
* Un nuage de mot illustrant les termes les plus important en fonction de leur taille, généré à partir de l'algorithme TF-IDF
* Une liste des tweets les plus significatifs, dont l'indice TF-IDF est le plus grand

## Lancement du script

Lors du lancement du script il suffit d'indiquer les 2 paramètres suivant :
* le mot clé choisi
* le nombre de tweets à récupérer

```bash
python3 main.py test 100
```

## Les librairie utilisées

```python
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
```
