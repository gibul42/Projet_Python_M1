from Document import RedditDocument, ArxivDocument

class DocumentFactory:
    @staticmethod
    def create_document(doc_type, **kwargs):
        """
        doc_type : 'reddit' ou 'arxiv'
        kwargs : paramètres nécessaires pour le constructeur
        """
        if doc_type.lower() == "reddit":
            # RedditDocument(titre, auteur, date, url, texte, nb_commentaires)
            return RedditDocument(
                kwargs.get("titre"),
                kwargs.get("auteur"),
                kwargs.get("date"),
                kwargs.get("url"),
                kwargs.get("texte"),
                kwargs.get("nb_commentaires", 0)
            )
        elif doc_type.lower() == "arxiv":
            # ArxivDocument(titre, auteurs, date, url, texte)
            return ArxivDocument(
                kwargs.get("titre"),
                kwargs.get("auteurs", []),
                kwargs.get("date"),
                kwargs.get("url"),
                kwargs.get("texte")
            )
        else:
            raise ValueError(f"Type de document inconnu : {doc_type}")

factory = DocumentFactory()

"""# Création d’un RedditDocument
doc1 = factory.create_document(
    "reddit",
    titre="Post test Reddit",
    auteur="user_test",
    date="2025-11-06",
    url="https://reddit.com/test",
    texte="Contenu du post Reddit",
    nb_commentaires=12
)

# Création d’un ArxivDocument
doc2 = factory.create_document(
    "arxiv",
    titre="Article test Arxiv",
    auteurs=["Alice", "Bob"],
    date="2025-01-01",
    url="https://arxiv.org/abs/0000.0000",
    texte="Résumé de l'article"
)

print(doc1)  # [Reddit] Post test Reddit (12 commentaires)
print(doc2)  # [Arxiv] Article test Arxiv – Auteurs : Alice, Bob"""

