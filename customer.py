#!/usr/bin/env python3

import sqlite3
from utils import *
from pretty_table import PrettyTable

class Customer_Session:
    def __init__(self, database):
        self.cid = None
        self.connection = sqlite3.connect(database)
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

    # def sql_search_keyword(self, keywords):
        # query = 'select pid, name, unit, count(name) from ( '
        # subqueries = []
        # for kwd in keywords:
            # if not kwd.isalpha():
                # print('Error: illegal character found in keywords')
                # return None
            # subqueries.append(' select * from products'
                    # ' where name like \'%{}%\''.format(kwd))
        # query = query + ' union all'.join(subqueries) + \
                # ' )group by name order by count(name) desc;'
        # self.cursor.execute(query)
        # return self.cursor.fetchall()

    # def sql_search_keyword(self, keywords):
        # patterns = []
        # for kwd in keywords:
            # patterns.append('%{}%'.format(kwd))
        # query = 'SELECT pid, name, unit, COUNT(name) FROM (' + \
                # ' UNION ALL '.join(
                        # 'SELECT * FROM products WHERE name LIKE ?' for \
                                # _ in keywords
                        # ) \
                # + ') GROUP BY name ORDER BY COUNT(name) DESC;'
        # self.cursor.execute(query, patterns)
        # return self.cursor.fetchall()


    # def print_product(self, products):

    def search_for_prodects(self):
        while True:
            clear_screen()
            print('Please enter keywords:')
            search_input = input('> ')
            if search_input != '':
                keywords = search_input.strip().split()

                # Check if keywords contain illegal characters:
                for kwd in keywords:
                    if not kwd.isalpha():
                        print('Error: illegal character found in keywords')
                        continue

                self.cursor.execute(
                        'CREATE VIEW search_result AS ' + \
                        'SELECT pid, name, unit, COUNT(name) FROM ( ' + \
                        ' UNION ALL '.join(
                            'SELECT * FROM products WHERE name LIKE \'%{}%\''.format(kwd) \
                            for kwd in keywords
                        ) + \
                        ') GROUP BY name ORDER BY COUNT(name) DESC;'
                )
                self.cursor.execute(
                        '''
                        SELECT s.pid, s.name, s.unit, COUNT(DISTINCT c1.sid),
                            COUNT(DISTINCT c2.sid), MIN(c1.uprice),
                            MIN(c2.uprice)
                        FROM search_result s, carries c1, carries c2
                        WHERE s.pid = c1.pid
                            AND s.pid = c2.pid
                            AND c2.qty > 0
                        GROUP BY s.pid;
                        '''
                )
                product_detail = self.cursor.fetchall()
                self.cursor.execute(
                        '''
                        SELECT s.pid, COUNT(DISTINCT ol.oid)
                        FROM search_result s, orders od, olines ol
                        WHERE s.pid = ol.pid
                            AND ol.oid = od.oid
                            AND od.odate >= (SELECT DATE('now', '-7 day'))
                        GROUP BY s.pid;
                        '''
                )
                product_orders = self.cursor.fetchall()

                # TODO: if result contains more than 5 lines...
                table = PrettyTable(8)
                col_name = ['Product ID', 'Product Name', 'Unit',
                        'Num. of Stores Carry', 'Num. of Stores In Stock',
                        'Min. Price Carry', 'Min. Price In Stock',
                        'Num. of Orders Past 7 Days']
                underline = ['-'*len(s) for s in col_name]
                table.writeLine(col_name)
                table.writeLine(underline)
                products = []
                for row in product_detail:
                    # pid, name, unit, ncarry, nstock, pcarry, pstock = row
                    row = list(row)
                    pid = row[0]
                    norder = 0
                    for line in product_orders:
                        if line[0] == pid:
                            norder = line[1]
                    row.append(norder)
                    products.append(row)
                    table.writeLine([str(r) for r in row])

                while True:
                    clear_screen()
                    print(table)
                    print('What would you like to do next?')
                    print('1. See product details')
                    print('2. Add product to cart')
                    print('3. Go back')
                    option = input('> ')
                    clear_screen()
                    print(table)
                    if option == '1':
                        self.see_product_details()
                    elif option == '2':
                        self.add_to_cart(products)
                    elif option == '3':
                        break

                self.cursor.execute(
                        '''
                        DROP VIEW search_result;
                        '''
                )
                break

    def see_product_details(self):
        self.cursor.execute(
                '''
                SELECT s.pid, s.name, s.unit, c.name
                FROM search_result s, products p, categories c
                WHERE s.pid = p.pid
                    AND p.cat = c.cat;
                '''
        )
        product_detail = self.cursor.fetchall()
        self.cursor.execute(
                '''
                SELECT s.pid, stores.name, carries.uprice, carries.qty, stores.sid
                FROM search_result s, carries, stores
                WHERE s.pid = carries.pid
                    AND carries.sid = stores.sid;
                '''
        )
        store_detail = self.cursor.fetchall()
        self.cursor.execute(
                '''
                SELECT sid, COUNT(DISTINCT olines.oid)
                FROM olines, orders
                WHERE olines.oid = orders.oid
                    AND orders.odate >= (SELECT DATE('now', '-7 day'))
                GROUP BY sid;
                '''
        )
        orders = self.cursor.fetchall()
        orders_d = {}
        for sid, norder in orders:
            orders_d[sid] = norder

        table = PrettyTable(8)
        col_name = ['Product ID', 'Product Name', 'Unit',
                'Category', 'Available In', 'Unit Price', 'Quantities Left',
                'Num. of Orders Past 7 Days']
        underline = ['-'*len(s) for s in col_name]
        table.writeLine(col_name)
        table.writeLine(underline)
        for product_row in product_detail:
            product_row = list(product_row)
            pivot_row = True
            for store_row in store_detail:
                store_row = list(store_row)
                if product_row[0] == store_row[0]:
                    sid = store_row[-1]
                    norders = orders_d[sid] if sid in orders_d else 0
                    if pivot_row:
                        row = product_row + store_row[1:-1] + [norders]
                    else:
                        row = [' ' for _ in product_row] + store_row[1:-1] + [norders]
                    table.writeLine([str(s) for s in row])
                    pivot_row = False

        clear_screen()
        print(table)

        while True:
            print('What would you like to do next?')
            print('1. Go back')
            option = input('> ')
            clear_screen()
            print(table)
            if option == '1':
                return

    def add_to_cart(self, products):
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
    customer_session = Customer_Session('./database.db')
    customer_session.start_session('yan')
    customer_session.close()

if __name__ == '__main__':
    test()
