import re
import pandas as pd
from Document import Document

class Corpus:
    _instance = None   # Singleton

    def __new__(cls, nom):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
        return cls._instance

    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0

        # TD6 additions
        self.big_text = None       
        self.vocabulaire = None    
        self.freq = None           

    # ---------------------------------------------------------
    # AJOUT DOCUMENT
    # ---------------------------------------------------------
    def addDocument(self, doc, author_obj):
        self.id2doc[self.ndoc] = doc
        doc_id = self.ndoc
        self.ndoc += 1

        # Auteurs
        if author_obj.name not in self.authors:
            self.authors[author_obj.name] = author_obj
            self.naut += 1

        self.authors[author_obj.name].add(doc_id, doc)

        # Reset pour TD6 / TD7
        self.big_text = None
        self.freq = None
        self.vocabulaire = None

    # ---------------------------------------------------------
    # SAUVEGARDE / CHARGEMENT
    # ---------------------------------------------------------
    def save(self, filename):
        df = pd.DataFrame([
            [i, d.titre, d.auteur, d.date, d.url, d.texte, d.type]
            for i, d in self.id2doc.items()
        ], columns=["id", "titre", "auteur", "date", "url", "texte", "type"])
        df.to_csv(filename, sep="\t", index=False)

    def load(self, filename):
        df = pd.read_csv(filename, sep="\t")
        return df

    def __repr__(self):
        return f"Corpus {self.nom}: {self.ndoc} documents, {self.naut} auteurs"

    # ---------------------------------------------------------
    # TD6 - PARTIE 1 : REGEX
    # ---------------------------------------------------------
    def build_big_text(self):
        if self.big_text is None:
            # join in insertion order; preserve spaces
            self.big_text = " ".join([d.texte for d in self.id2doc.values()])
        return self.big_text

    def search(self, motif):
        txt = self.build_big_text()
        pattern = re.compile(motif, re.IGNORECASE)
        return pattern.findall(txt)

    def concorde(self, motif, taille=30):
        txt = self.build_big_text()
        pattern = re.compile(motif, re.IGNORECASE)

        lignes = []
        for m in pattern.finditer(txt):
            start, end = m.start(), m.end()
            gauche = txt[max(0, start - taille): start]
            droite = txt[end: end + taille]
            lignes.append([gauche, txt[start:end], droite])

        df = pd.DataFrame(lignes, columns=["contexte_gauche", "motif_trouve", "contexte_droit"])
        return df

    # ---------------------------------------------------------
    # TD6 - PARTIE 2 : STATISTIQUES
    # ---------------------------------------------------------
    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        # remove digits
        texte = re.sub(r"[0-9]", " ", texte)
        # replace punctuation with spaces
        texte = re.sub(r"[.,;:!?()\[\]{}\/\\'\"—\-–]", " ", texte)
        texte = re.sub(r"\s+", " ", texte)
        return texte.strip()

    def construire_stats(self):
        vocab_set = set()
        compteur = {}
        docfreq = {}

        for doc in self.id2doc.values():
            txt = self.nettoyer_texte(doc.texte)
            mots = txt.split()

            mots_uniques = set(mots)

            for m in mots:
                compteur[m] = compteur.get(m, 0) + 1

            for m in mots_uniques:
                docfreq[m] = docfreq.get(m, 0) + 1

            vocab_set.update(mots)

        vocab = sorted(list(vocab_set))
        self.vocabulaire = vocab

        self.freq = pd.DataFrame({
            "mot": vocab,
            "term_frequency": [compteur[m] for m in vocab],
            "document_frequency": [docfreq[m] for m in vocab]
        }).sort_values(by="term_frequency", ascending=False)

    def stats(self, n=20):
        if self.freq is None:
            self.construire_stats()

        print("Nombre de mots différents :", len(self.vocabulaire))
        print("\nMots les plus fréquents :")
        print(self.freq.head(n))

    # utilitaire : récupérer document par id
    def get_document(self, doc_id):
        return self.id2doc.get(doc_id, None)
