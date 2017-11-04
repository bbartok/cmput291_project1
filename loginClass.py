import sqlite3


class Customer:

    def __init__(self):
        
        self.cid        = None
        self.pwd        = None
        self.connection = sqlite3.connect('./database.db')
        self.cursor     = self.connection.cursor()
        
        self.cursor.execute('PRAGMA foreign_keys=ON;')

    def validate_session(self,cid,pwd):

        Valid_bool = False
        self.cid   = str(cid)
        self.pwd   = str(pwd)
        params = (cid,)
        
        valid_query  = 'SELECT cid, pwd FROM customers WHERE cid=(?)'
        self.cursor.execute(valid_query, params)
        queryResult  = self.cursor.fetchall()
        try:
            valid_cid = queryResult[0][0]
            valid_pwd = queryResult[0][1]
        except ValueError and IndexError:
            self.connection.commit()
            self.connection.close()
            return Valid_bool

        if valid_cid == self.cid:
            if valid_pwd == self.pwd:
                Valid_bool = True

        self.connection.commit()
        self.connection.close()
                
        return Valid_bool
    
    def add_customer(self,cid,name,address,pwd):

        failed_bool = False
        params = (cid, name, address, pwd)
        add_query = 'INSERT INTO customers VALUES (?,?,?,?)'
        try:
            self.cursor.execute(add_query, params)
        except sqlite3.IntegrityError:
            failed_bool = True           
            
        self.connection.commit()
        self.connection.close()
        return failed_bool
        
    
