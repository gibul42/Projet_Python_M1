import praw
import pandas as pd
import urllib.request
import ssl
import xmltodict
import os

data = []


def corpus_redit():

    reddit = praw.Reddit(
        client_id='DNRXo8NPa6OMRFGifCP7ug',
        client_secret='GBmiInh5G9lSr6vEYEk8y_mDjbnFEQ',
        user_agent='TD003'
    )

    submission = reddit.submission(id="a3p0uq")
    submission.comments.replace_more(limit=0)
    sub = reddit.subreddit('MachineLearning')
    identifiant = len(data)
    for post in sub.hot():
        data.append([identifiant, post.selftext , "reddit"])
        identifiant += 1
    return data


def corpus_arxiv():
    ctx = ssl._create_unverified_context()
    xml_brut = urllib.request.urlopen("http://export.arxiv.org/api/query?search_query=all:Machine+learning" , context=ctx)
    xml_dict = xmltodict.parse(xml_brut.read())
    identifiant = len(data)
    for i in range(len(xml_dict['feed']["entry"])):
        data.append([identifiant, xml_dict['feed']["entry"][i]["summary"], "arxiv"])
    
        identifiant +=1
    return data


fichier_csv = "textes.csv"

if os.path.exists(fichier_csv):
    print("exist")
    dataFrame = pd.read_csv(fichier_csv, sep="\t", encoding="utf-8")

else:

    corpus_arxiv()
    corpus_redit()

    dataFrame = pd.DataFrame(data, columns=["id", "texte", "origine"])

    dataFrame.to_csv(fichier_csv, index=False, sep="\t", encoding="utf-8")


taille_corpus = len(dataFrame)
print(taille_corpus)

