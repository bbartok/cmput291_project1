#Created by Brendan Bartok on 2017-11-03
import sqlite3

#####################################################################################
# Class has two purposes. The first, seen in the validate_session function, validates
# the customers cid and pwd, confirming they are correct. The second, add_customer,
# creates a customer account for the user.
######################################################################################
class Customer:

    def __init__(self, database):
        
        self.cid        = None                          #initializes cid variable
        self.pwd        = None                          #initializes pwd variable
        self.connection = sqlite3.connect(database)     #connects to database
        self.cursor     = self.connection.cursor()      #sets ups cursor
        
        self.cursor.execute('PRAGMA foreign_keys=ON;')  #allows foreign keys

        
    ####################################################
    # This function validates the customers cid and pwd
    # and returns a boolean variable
    ####################################################
    def validate_session(self,cid,pwd):

        Valid_bool = False          #initizializes boolean variable to False
        self.cid   = str(cid)       #applies cid as a string
        self.pwd   = str(pwd)       #applies pwd as a string
        params = (cid,)             #sets up parameters for query
        
        valid_query  = 'SELECT cid, pwd FROM customers WHERE cid=(?)'      #template for query
        self.cursor.execute(valid_query, params)                            #executes query
        queryResult  = self.cursor.fetchall()                               #retrieves results
        try:                                             #splits query results into two variables instead of a list of tuples
            valid_cid = queryResult[0][0]
            valid_pwd = queryResult[0][1]
        except ValueError and IndexError:                #Error check for if cid and pwd exist
            self.connection.commit()
            self.connection.close()
            return Valid_bool

        if valid_cid == self.cid:                       #confirms that cid and pwd are correct then sets Valid_bool to True
            if valid_pwd == self.pwd:
                Valid_bool = True

        self.connection.commit()                        #commits and closes databae
        self.connection.close()
                
        return Valid_bool                               #returns boolean
    
    ######################################################################
    # This function adds a customer into the customer tables. It takes in
    # a username (cid), a name of user, an address, and a password. It has 
    # and returns a boolean value to ensure that the insertion into the db 
    # went successfully.
    ######################################################################
    
    def add_customer(self,cid,name,address,pwd):

        failed_bool = False                         #error check boolean initilized
        params = (cid, name, address, pwd)          #parameters for query are set up
        add_query = 'INSERT INTO customers VALUES (?,?,?,?)'    #query template set up
        try:                                            # try loop to execute the query
            self.cursor.execute(add_query, params)      ########################################################################
        except sqlite3.IntegrityError:                  # catches an integrity error, setting the failure boolean to true
            failed_bool = True                          # This causes the user to have to reenter a different cid, because 
                                                        # it is already in use.
                                                        ########################################################################
        self.connection.commit()                    #commits and closes db
        self.connection.close()
        return failed_bool                          #returns the failure boolean
        
    
