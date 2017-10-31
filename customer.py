#!/usr/bin/env python3

import sqlite3
from utils import *
from pretty_table import PrettyTable

class Customer_Session:
    def __init__(self):
        self.cid = None
        self.connection = sqlite3.connect('./database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys=ON;')

    def start_session(self, cid):
        """
        Main interface, called from login system
        """
        self.cid = cid
        clear_screen()
        print ('Customer session started.')
        while True:
            print ('Welcome, {}. What would you like to do today?'.format(cid))
            print ('1. Search for products')
            print ('2. Place an order')
            print ('3. List orders')
            print ('4. Logout')
            choice = input('> ')
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
            clear_screen()

    def search_keyword(self, keywords):
        query = 'select pid, name, unit, count(name) from ( '
        subqueries = []
        for kwd in keywords:
            if not kwd.isalpha():
                print('Illegial character found in keywords')
                return False
            subqueries.append(' select * from products'
                    ' where name like \'%{}%\''.format(kwd))
        query = query + ' union all'.join(subqueries) + \
                ' )group by name order by count(name) desc;'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def print_product(self, products):
        table = PrettyTable(3)
        table.writeLine(['Product ID', 'Product Name', 'Unit'])
        table.writeLine(['----------', '------------', '----'])
        for pid, name, unit, _ in products:
            table.writeLine([pid, name, unit])
        print(table)

    def search_for_prodects(self):
        while True:
            clear_screen()
            print('Please enter keywords:')
            search_input = input('> ')
            if search_input != '':
                keywords = search_input.strip().split()
                products = self.search_keyword(keywords)
                if products != None:
                    self.print_product(products)
                input('> ')
                break

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
    customer_session.close()

if __name__ == '__main__':
    test()
