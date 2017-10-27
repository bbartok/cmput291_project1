import sqlite3

class Customer_Session:
    def __init__(self):
        self.cid = None
        self.connection = sqlite3.connect('./database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys=ON;')

    def start_session(self, cid):
        self.cid = cid
        print ('Customer session started.')
        print ('Welcome, {}!'.format(cid))

        while True:
            print ('1. Search for products')
            print ('2. Place an order')
            print ('3. List orders')
            print ('4. Logout')
            choice = input('What would you like to do today? > ')
            if choice == '1':
                self.search_for_prodects()
            elif choice == '2':
                self.place_an_order()
            elif choice == '3':
                self.list_orders()
            elif choice == '4':
                print ('Logging you out, have a nice day!')
                self.cid = None
                print ('Customer session ended.')
                break

    def search_for_prodects(self):
        pass

    def place_an_order(self):
        pass

    def list_orders(self):
        pass

    def close(self):
        """
        Call this function at the end of the program.
        """
        self.connection.commit()
        self.connection.close()

def test():
    customer_session = Customer_Session()
    customer_session.start_session('yan')

if __name__ == '__main__':
    test()
