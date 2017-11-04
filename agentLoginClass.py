import sqlite3

class Agent:

    def __init__(self):

        self.connection = sqlite3.connect('./database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys=ON;')

    def validate_agent(self, aid, pwd):

        Valid_bool = False

        params = (aid,)

        valid_query = 'SELECT aid, pwd FROM agents WHERE aid=(?)'
        self.cursor.execute(valid_query, params)
        queryResult = self.cursor.fetchall()
        
        try:
            valid_aid = queryResult[0][0]
            valid_pwd = queryResult[0][1]
        except ValueError and IndexError:
            self.connection.commit()
            self.connection.close()
            return Valid_bool

        if valid_aid == str(aid):
            if valid_pwd == str(pwd):
                Valid_bool = True

        self.connection.commit()
        self.connection.close()

        return Valid_bool

        
            
