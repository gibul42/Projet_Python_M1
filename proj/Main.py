import praw
import pandas as pd
import urllib.request
import ssl
import xmltodict
import os
from datetime import datetime
from tqdm import tqdm

from Corpus import Corpus
from Author import Author
from factory import DocumentFactory
from search_engine import SearchEngine

factory = DocumentFactory()
corpus = Corpus("MonCorpus")


# ============================================================
# 1) FONCTION : Récupération Reddit
# ============================================================
def corpus_reddit(keyword):
    reddit = praw.Reddit(
        client_id='DNRXo8NPa6OMRFGifCP7ug',
        client_secret='GBmiInh5G9lSr6vEYEk8y_mDjbnFEQ',
        user_agent='TD003'
    )

    sub = reddit.subreddit(keyword)
    data_local = []
    try :
        for post in tqdm(sub.hot(limit=20), desc = "Recupération Reddit ", ncols= 100, ascii= True):        # limite raisonnable
            texte = post.selftext.replace("\n", " ")
            titre = post.title
            auteur = str(post.author) if post.author else "unknown"
            date = datetime.fromtimestamp(post.created)
            url = post.url
            nb_comments = post.num_comments

            # enregistrer en mémoire
            data_local.append(["reddit", titre, auteur, date, url, texte, nb_comments])
    except :
        pass
    return data_local


# ============================================================
# 2) FONCTION : Récupération Arxiv
# ============================================================
def corpus_arxiv(keyword):
    ctx = ssl._create_unverified_context()
    url = "http://export.arxiv.org/api/query?search_query=all:"+keyword.replace(" ", "+")
    xmldata = urllib.request.urlopen(url, context=ctx)
    xml_dict = xmltodict.parse(xmldata.read())

    data_local = []

    entries = xml_dict['feed']["entry"]
    try :
        for entry in tqdm(entries, desc = "Recupération Arxiv", ncols= 100, ascii= True):
            titre = entry["title"]
            auteur = entry["author"]["name"] if "name" in entry["author"] else "unknown"
            date = datetime.strptime(entry["published"], "%Y-%m-%dT%H:%M:%SZ")
            url = entry["id"]
            texte = entry["summary"].replace("\n", " ")
            coauthors = []

            # Si plusieurs auteurs
            if isinstance(entry["author"], list):
                coauthors = [a["name"] for a in entry["author"]]
            else:
                coauthors = [entry["author"]["name"]]

            data_local.append(["arxiv", titre, auteur, date, url, texte, coauthors])
    except :
        pass

    return data_local


# ============================================================
# 3) CHARGEMENT OU RÉCUPÉRATION DES DONNÉES
# ============================================================
fichier_csv = "textes.csv"
query = "Alan"
if os.path.exists(fichier_csv+"x"):
    print("Chargement du fichier déjà existant…")
    df = pd.read_csv(fichier_csv, sep="\t", encoding="utf-8")
else:
    print("Téléchargement depuis Reddit + Arxiv…")
    data = []

    # Récupération Arxiv
    for entry in corpus_arxiv(query):
        data.append(entry)

    # Récupération Reddit
    for entry in corpus_reddit(query):
        data.append(entry)

    # Enregistrement CSV
    df = pd.DataFrame(data, columns=[
        "source", "titre", "auteur", "date", "url", "texte", "extra"
    ])

    df.to_csv(fichier_csv, index=False, sep="\t", encoding="utf-8")


# ============================================================
# 4) NETTOYAGE : suppression documents trop courts
# ============================================================
df = df.dropna()
df = df[df["texte"].apply(lambda x: len(str(x)) > 20)]


# ============================================================
# 5) CONSTRUCTION DU CORPUS AVEC LES CLASSES TD4–TD5
# ============================================================
for i, row in df.iterrows():

    source = row["source"]
    titre = row["titre"]
    auteur = row["auteur"]
    date = row["date"]
    url = row["url"]
    texte = row["texte"]
    extra = row["extra"]

    # Création auteur
    if auteur not in [None, "None"]:
        aut = Author(str(auteur))
    else:
        aut = Author("unknown")

    # Création du document via Factory
    if source == "reddit":
        doc = factory.create("reddit", titre, auteur, date, url, texte, int(extra))

    elif source == "arxiv":
        # extra contient la liste des co-auteurs
        if isinstance(extra, str):
            coauthors = [extra]
        else:
            coauthors = extra

        doc = factory.create("arxiv", titre, auteur, date, url, texte, coauthors)

    else:
        continue

    # Ajout dans le corpus
    corpus.addDocument(doc, aut)


# Sauvegarde du corpus structuré TD4
corpus.save("corpus.csv")

print("\nCorpus construit :", corpus)


# ============================================================
# 6) CRÉATION MOTEUR DE RECHERCHE (TD7)
# ============================================================
engine = SearchEngine(corpus)


print("\nRecherche :", query)
results = engine.search(query, k=5)

print("\nRésultats :")
print(results)
