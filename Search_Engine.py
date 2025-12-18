import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from tqdm import tqdm

class SearchEngine:
    def __init__(self, corpus, use_tfidf=True):
        
        self.corpus = corpus
        self.use_tfidf = use_tfidf

        # Construire vocabulaire et matrices si nécessaire
        if self.corpus.vocab is None:
            self.corpus.construire_vocab()
        if not hasattr(self.corpus, 'mat_TF'):
            self.corpus.build_mat_TF()
        if not hasattr(self.corpus, 'mat_TFxIDF'):
            self.corpus.build_mat_TFxIDF()

        # Choix de la matrice à utiliser
        self.mat = self.corpus.mat_TFxIDF if self.use_tfidf else self.corpus.mat_TF
        self.mat_csr = self.mat.tocsr()
        self.vocab = self.corpus.vocab
        self.id2mot = {data["id"]: mot for mot, data in self.vocab.items()}

    def search(self, mots_clefs, top_k=5):

        # Construire le vecteur requête
        vect_req = np.zeros(len(self.vocab), dtype=np.float32)
        for mot in tqdm(mots_clefs,  desc="Processing", leave=False):
            mot = mot.lower()
            if mot in self.vocab:
                vect_req[self.vocab[mot]["id"]] = 1  # fréquence = 1 pour présence simple

        # Calculer similarité cosinus
        scores = []
        for i in tqdm(range(self.mat_csr.shape[0]),  desc="Processing", leave=False):
            doc_vect = self.mat_csr[i].toarray().flatten()
            num = np.dot(vect_req, doc_vect)
            denom = np.linalg.norm(vect_req) * np.linalg.norm(doc_vect)
            sim = num / denom if denom != 0 else 0
            scores.append((i, sim))

        # Trier par score décroissant
        scores.sort(key=lambda x: x[1], reverse=True)

        # Construire DataFrame résultat
        rows = []
        for i, score in tqdm(scores[:top_k],  desc="Processing", leave=False):
            doc = list(self.corpus.id2doc.values())[i]
            rows.append({
                "Titre": doc.titre,
                "Source": doc.getType(),
                "Score": score
            })

        return pd.DataFrame(rows)
