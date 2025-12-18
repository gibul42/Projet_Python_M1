import os
import ssl
import urllib.request
import xmltodict
import praw
from datetime import datetime
from Corpus import Corpus
from Document import RedditDocument, ArxivDocument
from SearchEngine import SearchEngine

corpus = Corpus("Machine Learning")

def corpus_reddit():
    reddit = praw.Reddit(
        client_id='DNRXo8NPa6OMRFGifCP7ug',
        client_secret='GBmiInh5G9lSr6vEYEk8y_mDjbnFEQ',
        user_agent='TD003'
    )

    sub = reddit.subreddit("Machine Learning")
    for post in sub.hot(limit=20):
        texte = post.selftext.replace("\n", " ")
        doc = RedditDocument(
            post.title,
            str(post.author),
            datetime.fromtimestamp(post.created),
            post.url,
            texte,
            post.num_comments
        )
        corpus.add_doc(doc)

def corpus_arxiv():
    ctx = ssl._create_unverified_context()
    url = "http://export.arxiv.org/api/query?search_query=all:machine+learning"
    xml = urllib.request.urlopen(url, context=ctx)
    data = xmltodict.parse(xml.read())

    for entry in data["feed"]["entry"][:20]:
        #data.append([identifiant, xml_dict['feed']["entry"][i]["summary"], "arxiv"])
        auteurs = [a["name"] for a in entry["author"]]
        doc = ArxivDocument(
            entry["title"],
            auteurs,
            datetime.strptime(entry["published"], "%Y-%m-%dT%H:%M:%SZ"),
            entry["id"],
            entry["summary"]
        )
        corpus.add_doc(doc)

if not os.path.exists("textes.csv"):
    corpus_reddit()
    corpus_arxiv()
    corpus.save("textes.csv")

df = corpus.load("textes.csv")

print("Taille du corpus :", len(df))

for i in range(len(df)):
    texte = df["texte"][i]
    print(len(texte.split()), "mots /", len(texte.split(".")), "phrases")

df = df[df["texte"].str.len() >= 20]

big_string = " ".join(df["texte"].tolist())

engine = SearchEngine(corpus)
print(engine.search("machine ", 5))
