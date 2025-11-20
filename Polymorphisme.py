from Document import Document, RedditDocument, ArxivDocument
from Corpus import Corpus


# --- Création de quelques documents ---
"""doc1 = RedditDocument(
    titre="Deep Learning is awesome!",
    auteur="user123",
    date="2025-11-06",
    url="https://reddit.com/r/MachineLearning/",
    texte="Voici un post intéressant sur le deep learning...",
    nb_commentaires=42
)

doc2 = ArxivDocument(
    titre="A Comprehensive Survey on Transformers",
    auteurs=["Vaswani", "Shazeer", "Parmar"],
    date="2017-06-01",
    url="https://arxiv.org/abs/1706.03762",
    texte="Cet article présente le modèle Transformer..."
)"""

# --- Création du corpus ---
id2doc = {0: doc1, 1: doc2}
auteurs = ["user123", "Vaswani", "Shazeer", "Parmar"]
mon_corpus = Corpus("TestCorpus", auteurs, id2doc)

# --- Test du polymorphisme ---
for identifiant, document in mon_corpus.id2doc.items():
    print(f"Document ID: {identifiant}")
    print(document)        # Appelle __str__ selon le type réel de l’objet
    print(type(document))  # Affiche la classe réelle (RedditDocument ou ArxivDocument)
    print("-" * 50)
