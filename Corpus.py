import re
import pandas as pd
from collections import Counter
from scipy.sparse import csr_matrix
import numpy as np
from Document import RedditDocument, ArxivDocument
from tqdm import tqdm

class Corpus:

    def __init__(self, nom, authors, id2doc):
        self.nom = nom
        self.authors = authors
        self.id2doc = id2doc
        self.ndoc = len(id2doc)
        self.naut = len(authors)
        self._texte_concat = None
        self.vocab = None

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

        return pd.DataFrame(lignes, columns=["contexte_gauche", "motif_trouvé", "contexte_droit"])

    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        texte = re.sub(r"[^\w\s]", " ", texte)
        texte = re.sub(r"\d+", "", texte)
        texte = re.sub(r"\s+", " ", texte)
        return texte.strip()

    def construire_vocab(self):
        vocab = {}
        current_id = 0

        tous_les_mots = []
        mots_par_doc = []

        for doc in tqdm(self.id2doc.values(),  desc="Processing", leave=False):
            texte = self.nettoyer_texte(doc.texte)
            mots = texte.split()

            tous_les_mots.extend(mots)
            mots_par_doc.append(set(mots))

        compteur_tf = Counter(tous_les_mots)

        df_counts = {mot: 0 for mot in tqdm(compteur_tf, desc="Processing", leave=False)}
        for doc_set in tqdm(mots_par_doc, desc="Calcul DF", leave = False):
            for mot in doc_set:
                if mot in df_counts:
                    df_counts[mot] += 1

        for mot in tqdm(sorted(compteur_tf.keys()), desc="Processing", leave=False):
            vocab[mot] = {
                "id": current_id,
                "tf": compteur_tf[mot],
                "df": df_counts[mot]
            }
            current_id += 1

        self.vocab = vocab
        print(f"Vocabulaire construit : {len(vocab)} mots.")

    def stats(self, n=10):
        if self.vocab is None:
            self.construire_vocab()

        df = pd.DataFrame([
            {"mot": mot, "frequence": data["tf"], "document_frequency": data["df"]}
            for mot, data in self.vocab.items()
        ])

        print(f"Nombre de mots différents : {len(df)}")
        print(f"{n} mots les plus fréquents :")
        print(df.sort_values("frequence", ascending=False).head(n))

        return df

    def build_mat_TF(self):
        if self.vocab is None:
            self.construire_vocab()

        nb_docs = self.ndoc
        nb_mots = len(self.vocab)

        mot2id = {mot: data["id"] for mot, data in self.vocab.items()}

        rows = []
        cols = []
        values = []

        for i, doc in tqdm(enumerate(self.id2doc.values()), desc="Processing", leave=False):
            texte = self.nettoyer_texte(doc.texte)
            mots = texte.split()
            compteur = Counter(mots)

            for mot, freq in compteur.items():
                if mot in mot2id:
                    j = mot2id[mot]
                    rows.append(i)
                    cols.append(j)
                    values.append(freq)

        self.mat_TF = csr_matrix(
            (values, (rows, cols)),
            shape=(nb_docs, nb_mots),
            dtype=np.int32
        )

        print("Matrice TF construite.")
        print(f"Dimensions : {nb_docs} documents × {nb_mots} mots.")

    def build_mat_TFxIDF(self):
        if not hasattr(self, 'mat_TF'):
            self.build_mat_TF()

        nb_docs, nb_mots = self.mat_TF.shape

        # DF pour chaque mot
        df = np.array([self.vocab[mot]["df"] for mot in sorted(self.vocab.keys())], dtype=np.float32)

        # calcul IDF : log(N / df)
        idf = np.log(nb_docs / df)

        # multiplication TF * IDF
        # csr_matrix supporte multiplication élément par élément via broadcasting
        self.mat_TFxIDF = self.mat_TF.multiply(idf)

        print("Matrice TFxIDF construite.")
        print(f"Dimensions : {nb_docs} documents × {nb_mots} mots.")

    def recherche(self, mots_clefs, use_tfidf=False, top_k=5):
        if self.vocab is None:
            self.construire_vocab()
    
        # Choix de la matrice
        mat = self.mat_TFxIDF if use_tfidf else self.mat_TF
        mat_csr = mat.tocsr()  # s'assurer que c'est CSR pour accès par ligne
    
            # Construire le vecteur requête
        vect_req = np.zeros(len(self.vocab))
        for mot in mots_clefs:
            mot = mot.lower()
            if mot in self.vocab:
                vect_req[self.vocab[mot]["id"]] = 1  # ou fréquence si tu veux
    
        # Calcul de la similarité cosinus
        scores = []
        for i in tqdm(range(mat_csr.shape[0]), desc="Processing", leave=False):
            doc_vect = mat_csr[i].toarray().flatten()
            num = np.dot(vect_req, doc_vect)
            denom = np.linalg.norm(vect_req) * np.linalg.norm(doc_vect)
            sim = num / denom if denom != 0 else 0
            scores.append((i, sim))
    
        # Trier par score décroissant
        scores.sort(key=lambda x: x[1], reverse=True)
    
        # Afficher les résultats
        print(f"\nRésultats de recherche pour {mots_clefs} :")
        for i, score in scores[:top_k]:
            doc = list(self.id2doc.values())[i]
            print(f"{doc.titre} – Score : {score:.4f} – Source : {doc.getType()}")
    
        return scores
