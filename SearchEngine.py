import numpy as np
import pandas as pd
import math

class SearchEngine:
    def __init__(self, corpus):
        self.corpus = corpus
        self.vocab = {}
        self.build_vocab()
        self.build_tf_matrix()
        self.build_tfidf_matrix()


    def build_vocab(self):
        words = set()
        for doc in self.corpus.id2doc.values():
            words.update(self.corpus.nettoyer_texte(doc.texte).split())

        for i, word in enumerate(sorted(words)):
            self.vocab[word] = {
                "id": i,
                "tf": 0,
                "df": 0
            }

    def build_tf_matrix(self):
        n_docs = self.corpus.ndoc
        n_words = len(self.vocab)
        self.mat_tf = np.zeros((n_docs, n_words))

        for i, doc in self.corpus.id2doc.items():
            mots = self.corpus.nettoyer_texte(doc.texte).split()
            for mot in mots:
                j = self.vocab[mot]["id"]
                self.mat_tf[i, j] += 1

        for mot, info in self.vocab.items():
            j = info["id"]
            info["tf"] = self.mat_tf[:, j].sum()
            info["df"] = np.count_nonzero(self.mat_tf[:, j])

    def build_tfidf_matrix(self):
        n_docs = self.mat_tf.shape[0]
        self.mat_tfidf = np.zeros(self.mat_tf.shape)

        for mot, info in self.vocab.items():
            j = info["id"]
            idf = math.log((n_docs + 1) / (info["df"] + 1))
            self.mat_tfidf[:, j] = self.mat_tf[:, j] * idf

    def build_tfidf_matrix(self):
        n_docs = self.mat_tf.shape[0]
        self.mat_tfidf = np.zeros(self.mat_tf.shape)

        for mot, info in self.vocab.items():
            j = info["id"]
            idf = math.log((n_docs + 1) / (info["df"] + 1))
            self.mat_tfidf[:, j] = self.mat_tf[:, j] * idf

    def search(self, query, n=5):
        query_vec = np.zeros(len(self.vocab))
        mots = query.lower().split()

        for mot in mots:
            if mot in self.vocab:
                query_vec[self.vocab[mot]["id"]] += 1

        scores = []
        for i in range(self.mat_tfidf.shape[0]):
            score = np.dot(query_vec, self.mat_tfidf[i])
            scores.append(score)

        results = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:n]

        data = []
        for doc_id, score in results:
            doc = self.corpus.id2doc[doc_id]
            data.append([doc_id, doc.titre, doc.getType(), score])

        return pd.DataFrame(
            data,
            columns=["id", "titre", "source", "score"]
        )

