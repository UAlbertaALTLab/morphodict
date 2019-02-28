from sqlite3 import IntegrityError

"""
    This class is a simple wrapper around a SQLite3 connection
    To execute predefined queries
"""
class SqlSP():
    """
        Args:
            sqlConnection (SQLConnection): A SQLITE3 connection for the queries to run
    """
    def __init__(self, sqlConnection):
        self.sqlConnection = sqlConnection;

    def getCursor(self):
        return self.sqlConnection.cursor()

    """
        Insert a word
    """
    def addWord(self, id, context, language, type):
        cur = self.getCursor()
        cur.execute('''
            INSERT INTO [API_word] (id, context, language, type) VALUES (
            :id, 
            :context,
            :language,
            :type)
        ''', {"id": id, "context": context, "language": language, "type": type})
    
    """
        Insert a lemma
    """
    def addLemma(self, wordID):
        cur = self.getCursor()
        cur.execute('''
            INSERT INTO [API_lemma] (word_ptr_id) VALUES (
            :wordID)
        ''', {"wordID": wordID})

    """
        Insert an inflection
    """
    def addInflection(self, wordID, lemmaID):
        cur = self.getCursor()
        cur.execute('''
            INSERT INTO [API_inflection] (word_ptr_id, fk_lemma_id) VALUES (
            :wordID,
            :lemmaID)
        ''', {"wordID": wordID, "lemmaID": lemmaID})

    """
        Insert an inflection form
    """
    def addInflectionForm(self, id, name, inflectionID):
        cur = self.getCursor()
        cur.execute('''
            INSERT INTO [API_inflectionform] (id, name, fk_inflection_id) VALUES (
            :id,
            :name,
            :fk_inflection_id)
        ''', {"id": id, "name": name, "fk_inflection_id": inflectionID})

    """
        Insert a definition
    """
    def addDefinition(self, id, context, source, wordID):
        cur = self.getCursor()
        cur.execute('''
            INSERT INTO [API_definition] (id, context, source, fk_word_id) VALUES (
            :id,
            :context,
            :source,
            :wordID)
        ''', {"id": id, "context": context, "source": source, "wordID": wordID})

    """
        Insert an attribute
    """
    def addAttribute(self, id, name, lemmaID):
        cur = self.getCursor()
        cur.execute('''
            INSERT INTO [API_attribute] (id, name, fk_lemma_id) VALUES (
            :id,
            :name,
            :lemmaID)
        ''', {"id": id, "name": name, "lemmaID": lemmaID})
