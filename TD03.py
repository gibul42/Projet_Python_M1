import praw
import pandas as pd
import urllib.request
import ssl
import xmltodict
import os
from Document import Document
from datetime import datetime

data = []
id2doc = {}
id2aut = {}

#doc = Document("titre", "auteur", "date", "url", "texte")
#print(doc)
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
        data.append([identifiant, post.selftext.replace("\n", " ") , "reddit"])
        #print(datetime.fromtimestamp(post.created))
        id2doc[identifiant] = Document(post.title, post.author, datetime.fromtimestamp(post.created), post.url, post.selftext.replace("\n", " "))
        if post.author not in id2aut :
            id2aut[post.author] = []
        identifiant += 1
        #print(post)
    return data


def corpus_arxiv():
    ctx = ssl._create_unverified_context()
    xml_brut = urllib.request.urlopen("http://export.arxiv.org/api/query?search_query=all:Machine+learning" , context=ctx)
    xml_dict = xmltodict.parse(xml_brut.read())
    identifiant = len(data)
    for i in range(len(xml_dict['feed']["entry"])):
        #data.append([identifiant, xml_dict['feed']["entry"][i]["summary"], "arxiv"])
        print(datetime.strptime(xml_dict['feed']["entry"][i]["published"],"%Y-%m-%dT%H:%M:%SZ"))
        id2doc[identifiant] = Document(str(xml_dict['feed']["entry"][i]["title"]),str(xml_dict['feed']["entry"][i]["author"]),datetime.strptime(xml_dict['feed']["entry"][i]["published"],"%Y-%m-%dT%H:%M:%SZ"),str(xml_dict['feed']["entry"][i]["id"]),str(xml_dict['feed']["entry"][i]["summary"]))
        if  str(xml_dict['feed']["entry"][i]["author"]) not in id2aut :
            id2aut[str(xml_dict['feed']["entry"][i]["author"])] = []
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
    dataFrame.to_csv("texte.csv", index=False, sep="\t", encoding="utf-8")


taille_corpus = len(dataFrame)
#print(taille_corpus)
#print(dataFrame)

for i in range(taille_corpus):
    nbr_mot = len(dataFrame['texte'][i].split(' '))
    nbr_phrases = len(dataFrame['texte'][i].split('.'))
    if nbr_mot < 20 :
        dataFrame.drop([i], inplace=True)
        continue
    #doc.append[Document(dataFrame["titre"],dataFrame["auteur"],dataFrame["titre"],dataFrame["titre"])]
    
    #print(nbr_mot, nbr_phrases)

#print("taille", len(dataFrame), taille_corpus)

large_str = ","
large_str = large_str.join(dataFrame.astype(str).values.flatten())

print(id2doc)
#print(large_str)


