from Document import RedditDocument, ArxivDocument  # attention à la casse !

class CorpusSingleton:
    _instance = None

    def __new__(cls, nom, authors, id2doc):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.nom = nom
            cls._instance.authors = authors
            cls._instance.id2doc = id2doc
            cls._instance.ndoc = len(id2doc)
            cls._instance.naut = len(authors)
        return cls._instance

    def afficher_documents(self):
        for doc in self.id2doc.values():
            print(f"{doc.titre} – Source : {doc.getType()}")


# --- Création des objets fictifs ---
doc1 = RedditDocument("Post test Reddit", "user_test", "2025-11-06", "https://reddit.com/test", "Texte...", 12)
doc2 = ArxivDocument("Article test Arxiv", ["Alice", "Bob"], "2025-01-01", "https://arxiv.org/abs/0000.0000", "Résumé...")

id2doc = {0: doc1, 1: doc2}
authors = ["user_test", "Alice", "Bob"]

# Création du corpus Singleton
corpus1 = CorpusSingleton("CorpusUnique", authors, id2doc)
corpus2 = CorpusSingleton("AutreCorpus", [], {})

print(corpus1 is corpus2)  # True
corpus1.afficher_documents()
