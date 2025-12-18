import re
import pandas as pd
from collections import Counter

class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.id2doc = {}
        self.authors = {}
        self.ndoc = 0
        self.naut = 0

    def add_doc(self, doc):
        self.id2doc[self.ndoc] = doc

        if doc.auteur not in self.authors:
            from Author import Author
            self.authors[doc.auteur] = Author(doc.auteur)
            self.naut += 1

        self.authors[doc.auteur].add(self.ndoc, doc)
        self.ndoc += 1

    def show(self, n=5):
        for i, doc in list(self.id2doc.items())[:n]:
            print(doc, "-", doc.getType())

    def save(self, filename):
        data = []
        for i, doc in self.id2doc.items():
            data.append([i, doc.texte, doc.getType()])
        df = pd.DataFrame(data, columns=["id", "texte", "origine"])
        df.to_csv(filename, sep="\t", index=False)

    def load(self, filename):
        return pd.read_csv(filename, sep="\t")
    
    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        texte = re.sub(r"[0-9]", " ", texte)
        texte = re.sub(r"[^\w\s]", " ", texte)
        texte = re.sub(r"\s+", " ", texte)
        return texte.strip()
    
    def build_global_text(self):
        if not hasattr(self, "global_text"):
            self.global_text = " ".join(
                self.nettoyer_texte(doc.texte)
                for doc in self.id2doc.values()
            )
    def search(self, motif):
        self.build_global_text()
        pattern = re.compile(rf".{{0,40}}{motif}.{{0,40}}", re.IGNORECASE)
        return pattern.findall(self.global_text)

    def concorde(self, motif, context=30):
        self.build_global_text()
        rows = []

        for match in re.finditer(motif, self.global_text, re.IGNORECASE):
            start, end = match.span()
            left = self.global_text[max(0, start-context):start]
            right = self.global_text[end:end+context]
            rows.append([left, match.group(), right])

        return pd.DataFrame(rows, columns=["contexte_gauche", "motif", "contexte_droit"])

    def stats(self, n=10):
        vocab = Counter()
        doc_freq = Counter()

        for doc in self.id2doc.values():
            mots = self.nettoyer_texte(doc.texte).split()
            vocab.update(mots)
            doc_freq.update(set(mots))

        df = pd.DataFrame({
            "mot": vocab.keys(),
            "term_frequency": vocab.values(),
            "document_frequency": [doc_freq[m] for m in vocab.keys()]
        })

        print("Nombre de mots différents :", len(df))
        print("\nMots les plus fréquents :")
        print(df.sort_values("term_frequency", ascending=False).head(n))


