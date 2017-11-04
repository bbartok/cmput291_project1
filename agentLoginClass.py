import sqlite3

######################################################################
# Agent class is here solely to verify if the user has a correct aid
# and pwd. It does not write any information from user and does not return
# any information to user
######################################################################

class Agent:

    def __init__(self,database):                        #initializes class parameters

        self.connection = sqlite3.connect(database)     #connects to database
        self.cursor = self.connection.cursor()          #sets up database cursor
        self.cursor.execute('PRAGMA foreign_keys=ON;')  #allows foreign keys

    def validate_agent(self, aid, pwd):                 #program to validate agents aid and pwd, returns a boolean variable

        Valid_bool = False                              #initializes boolean to False

        params = (aid,)                                 #sets up a parameter for the query

        valid_query = 'SELECT aid, pwd FROM agents WHERE aid=(?)'   #creats a template for the validation query
        self.cursor.execute(valid_query, params)                    #adds the parameter i.e aid
        queryResult = self.cursor.fetchall()                        #stores the query results in variable
        
        try:                                                        #splits query results from list of tuple into two variables
            valid_aid = queryResult[0][0]
            valid_pwd = queryResult[0][1]
        except ValueError and IndexError:                           #catches error for if aid or pwd dont exist, then return boolean variable
            self.connection.commit()                                #commits and closes database
            self.connection.close()
            return Valid_bool

        if valid_aid == str(aid):                                   #checks if aid is correct
            if valid_pwd == str(pwd):                               #checks if pwd is correct
                Valid_bool = True                                   #if aid and pwd are correct, set valid boolean to true

        self.connection.commit()                                    #commit and close database
        self.connection.close()

        return Valid_bool                                           #returns boolean value

        
            
