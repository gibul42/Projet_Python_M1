import re
import pandas as pd

class Corpus:

    def __init__(self, nom, authors, id2doc):
        self.nom = nom 
        self.authors = authors
        self.id2doc = id2doc
        self.ndoc = len(id2doc)
        self.naut = len(authors)
        self._texte_concat = None

    def sort_by_date(self):
        self.id2doc = dict(sorted(self.id2doc.items(), key=lambda item: getattr(item[1], "date", "")))

    def build_concat(self):
        if self._texte_concat is None:
            print("Construction de la chaîne concaténée...")
            self._texte_concat = "\n".join([doc.texte for doc in self.id2doc.values()])
        return self._texte_concat

    def search(self, mot_cle):
        texte_total = self.build_concat()
        pattern = re.compile(rf"\b{mot_cle}\b", re.IGNORECASE)

        resultats = []
        for doc_id, doc in self.id2doc.items():
            if re.search(pattern, doc.texte):
                resultats.append((doc_id, doc.titre))
        
        return resultats

    def concorde(self, motif, contexte=5):
        lignes = []

        for doc_id, doc in self.id2doc.items():
            texte = doc.texte
            mots = re.findall(r"\w+|\W+", texte)
            for i, mot in enumerate(mots):
                if re.fullmatch(motif, mot, re.IGNORECASE):
                    gauche = ''.join(mots[max(0, i - contexte):i]).strip()
                    droit = ''.join(mots[i + 1:i + 1 + contexte]).strip()
                    lignes.append([gauche, mot, droit])

        df = pd.DataFrame(lignes, columns=["contexte_gauche", "motif_trouvé", "contexte_droit"])
        return df

    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        texte = re.sub(r"[^\w\s]", " ", texte)  # ponctuation → espace
        texte = re.sub(r"\d+", "", texte)        # supprime chiffres
        texte = re.sub(r"\s+", " ", texte)       # espaces multiples
        return texte.strip()

    def construire_vocabulaire(self):
        vocab_set = set()
        for doc in self.id2doc.values():
            texte_nettoye = self.nettoyer_texte(doc.texte)
            mots = texte_nettoye.split()
            vocab_set.update(mots)
        self.vocabulaire = {mot: 0 for mot in vocab_set}
        return self.vocabulaire

    def stats(self, n=10):
    # Construire le vocabulaire si ce n'est pas déjà fait
        if not hasattr(self, "vocabulaire"):
            self.construire_vocabulaire()
    # Concaténer tous les textes nettoyés
            texte_total = " ".join([self.nettoyer_texte(doc.texte) for doc in self.id2doc.values()])
    # Découper en mots
            mots = texte_total.split()
    # Construire un DataFrame Pandas pour compter les occurrences
            df = pd.DataFrame(mots, columns=["mot"])
            freq = df["mot"].value_counts().reset_index()
            freq.columns = ["mot", "frequence"]
        # DF : nombre de documents contenant chaque mot
        df_document = []
        for mot in freq["mot"]:
            count_doc = sum(1 for doc in self.id2doc.values() if mot in self.nettoyer_texte(doc.texte).split())
            df_document.append(count_doc)
        freq["document_frequency"] = df_document
    # Affichage
        print(f"Nombre de mots différents : {len(freq)}")
        print(f"{n} mots les plus fréquents :")
        print(freq.head(n))

        return freq  