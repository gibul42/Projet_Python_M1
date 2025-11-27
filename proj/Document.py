class Document:
    def __init__(self, titre, auteur, date, url, texte, doc_type="generic"):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.type = doc_type

    def __str__(self):
        return f"{self.titre}"

    def info(self):
        return (
            f"Titre: {self.titre}\n"
            f"Auteur: {self.auteur}\n"
            f"Date: {self.date}\n"
            f"URL: {self.url}\n"
            f"Texte: {self.texte}\n"
            f"Type: {self.type}"
        )


class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_comments):
        super().__init__(titre, auteur, date, url, texte, "reddit")
        self.nb_comments = nb_comments

    def getNbComments(self):
        return self.nb_comments

    def setNbComments(self, n):
        self.nb_comments = n

    def __str__(self):
        return f"[Reddit] {self.titre} ({self.nb_comments} commentaires)"


class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, coauthors):
        super().__init__(titre, auteur, date, url, texte, "arxiv")
        self.coauthors = coauthors

    def getCoauthors(self):
        return self.coauthors

    def setCoauthors(self, ca):
        self.coauthors = ca

    def __str__(self):
        return f"[Arxiv] {self.titre} | Co-auteurs: {', '.join(self.coauthors)}"
