import math
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

class SearchEngine:
    """
    SearchEngine construit les matrices TF et TFxIDF à partir d'un objet Corpus.
    - Le vocabulaire est un dictionnaire {mot: {id: int, term_frequency: int, document_frequency: int}}
    - mat_tf est une liste (len = N_docs) de dictionnaires {term_id: tf_in_doc}
    - mat_tfidf est une liste (len = N_docs) de dictionnaires {term_id: tfidf_weight}
    """

    def __init__(self, corpus):
        self.corpus = corpus
        # s'assurer que corpus a construit ses statistiques
        if self.corpus.vocabulaire is None or self.corpus.freq is None:
            self.corpus.construire_stats()

        # construire vocab avec infos
        self.vocab = {}  # mot -> info dict
        for idx, mot in enumerate(self.corpus.vocabulaire):
            # récupérer tf total et df depuis corpus.freq (DataFrame)
            row = self.corpus.freq[self.corpus.freq["mot"] == mot]
            if len(row) > 0:
                tf_total = int(row["term_frequency"].iloc[0])
                df = int(row["document_frequency"].iloc[0])
            else:
                tf_total = 0
                df = 0
            self.vocab[mot] = {"id": idx, "term_frequency": tf_total, "document_frequency": df}

        self.N = max(1, len(self.corpus.id2doc))  # nombre de documents
        # construire mat_tf (liste de dicts) et mat_tfidf
        self.mat_tf = []      # chaque entrée: {term_id: tf}
        for doc in tqdm(self.corpus.id2doc.values(), desc="Construction matrice TF", ncols= 100, ascii= True):
            txt = self.corpus.nettoyer_texte(doc.texte)
            mots = txt.split()
            tf_doc = {}
            for m in mots:
                if m in self.vocab:
                    tid = self.vocab[m]["id"]
                    tf_doc[tid] = tf_doc.get(tid, 0) + 1
            self.mat_tf.append(tf_doc)

        # calculer idf pour chaque term_id
        self.idf = {}
        for mot, info in self.vocab.items():
            df = info["document_frequency"]
            # éviter division par zéro
            if df > 0:
                self.idf[info["id"]] = math.log((self.N) / df, 10)  # base-10 log
            else:
                self.idf[info["id"]] = 0.0

        # construire mat_tfidf et pré-calculer les normes
        self.mat_tfidf = []
        self.doc_norms = []  # normes L2 des vecteurs tfidf
        for tf_doc in tqdm(self.mat_tf, desc="Construction matrice TF-IDF", ncols= 100, ascii= True):
            tfidf_doc = {}
            sq_sum = 0.0
            for tid, tf in tf_doc.items():
                w = tf * self.idf.get(tid, 0.0)
                tfidf_doc[tid] = w
                sq_sum += w * w
            norm = math.sqrt(sq_sum) if sq_sum > 0 else 0.0
            self.mat_tfidf.append(tfidf_doc)
            self.doc_norms.append(norm)

    def _query_to_vector(self, query, use_tfidf=True):
        """
        Transforme la requête (string) en vecteur dict {term_id: weight}.
        Si use_tfidf -> poids = tf_query * idf
        Sinon poids = tf_query
        """
        qtxt = self.corpus.nettoyer_texte(query)
        mots = qtxt.split()
        q_tf = {}
        for m in mots:
            if m in self.vocab:
                tid = self.vocab[m]["id"]
                q_tf[tid] = q_tf.get(tid, 0) + 1

        if use_tfidf:
            q_vec = {}
            sq = 0.0
            for tid, tf in q_tf.items():
                w = tf * self.idf.get(tid, 0.0)
                q_vec[tid] = w
                sq += w * w
            q_norm = math.sqrt(sq) if sq > 0 else 0.0
            return q_vec, q_norm
        else:
            # raw tf vector
            sq = sum(v * v for v in q_tf.values())
            q_norm = math.sqrt(sq) if sq > 0 else 0.0
            return q_tf, q_norm

    def _dot(self, vec1, vec2):
        # vec1, vec2 are dicts {tid: weight}; compute dot product
        if len(vec1) > len(vec2):
            vec1, vec2 = vec2, vec1
        s = 0.0
        for k, v in vec1.items():
            if k in vec2:
                s += v * vec2[k]
        return s

    def search(self, query, k=10, use_tfidf=True):
        """
        Exécute la recherche :
        - query : string de mots clés
        - k : nombre de documents à retourner
        - use_tfidf : si True, utilise TFxIDF pour vecteurs (recommandé)
        Retour : DataFrame pandas avec colonnes ['doc_id','titre','score','snippet']
        """
        q_vec, q_norm = self._query_to_vector(query, use_tfidf=use_tfidf)
        scores = []
        # sélectionner la matrice à utiliser
        mat = self.mat_tfidf if use_tfidf else self.mat_tf

        for doc_id, doc_vec in enumerate(mat):
            if q_norm == 0:
                score = 0.0
            else:
                num = self._dot(q_vec, doc_vec)
                denom = q_norm * (self.doc_norms[doc_id] if use_tfidf else math.sqrt(sum(v*v for v in doc_vec.values())))
                score = (num / denom) if denom != 0 else 0.0
            scores.append((doc_id, score))

        # trier par score décroissant
        scores.sort(key=lambda x: x[1], reverse=True)
        topk = scores[:k]

        rows = []
        for doc_id, score in topk:
            doc = list(self.corpus.id2doc.values())[doc_id]
            # snippet: extrait autour du premier terme de la requête s'il existe
            snippet = ""
            if len(query.strip()) > 0:
                raw = doc.texte
                q0 = self.corpus.nettoyer_texte(query).split()
                if len(q0) > 0:
                    tgt = q0[0]
                    pos = raw.lower().find(tgt)
                    if pos >= 0:
                        start = max(0, pos - 30)
                        snippet = raw[start: pos + 60].replace("\n", " ")
                    else:
                        snippet = raw[:100].replace("\n", " ")
                else:
                    snippet = raw[:100].replace("\n", " ")
            rows.append({
                "doc_id": doc_id,
                "titre": doc.titre,
                "score": score,
                "snippet": snippet
            })

        df = pd.DataFrame(rows)
        return df
