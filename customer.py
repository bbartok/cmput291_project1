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
        self.cart = []
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
                self.cart = []
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

                # TODO: bug, result doesn't in ordered
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
                self.cursor.execute(
                        '''
                        DROP VIEW search_result;
                        '''
                )

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
                    print('2. Go back')
                    option = input('> ')
                    clear_screen()
                    print(table)
                    if option == '1':
                        available_pids = [str(p) for p in list(zip(*products))[0]]
                        while True:
                            clear_screen()
                            print(table)
                            print('Please select a product ID (type nothing to go back):')
                            selection = input('> ')
                            if selection == '':
                                break
                            elif selection in available_pids:
                                self.see_product_details(selection)
                    elif option == '2':
                        break

                break

    def see_product_details(self, pid):
        self.cursor.execute(
                '''
                SELECT products.name, products.unit, categories.name,
                    stores.name, carries.uprice, carries.qty, stores.sid
                FROM products, categories, carries, stores
                WHERE products.cat = categories.cat
                    AND products.pid = carries.pid
                    AND carries.sid = stores.sid
                    AND products.pid = ?;
                ''',
                (pid, )
        )
        product_detail = self.cursor.fetchall()
        # self.cursor.execute(
                # '''
                # SELECT s.pid, stores.name, carries.uprice, carries.qty, stores.sid
                # FROM search_result s, carries, stores
                # WHERE s.pid = carries.pid
                    # AND carries.sid = stores.sid;
                # '''
        # )
        # store_detail = self.cursor.fetchall()
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

        detail_table = PrettyTable(4)
        col_name = ['Product ID', 'Product Name', 'Unit', 'Category']
        underline = ['-'*len(s) for s in col_name]
        detail_table.writeLine(col_name)
        detail_table.writeLine(underline)
        detail_table.writeLine([str(pid)] + [str(s) for s in list(product_detail[0])[:3]])

        store_table = PrettyTable(5)
        col_name = ['Select', 'Store', 'Price', 'Quantities Left',
                'Num. of Orders in 7 days']
        underline = ['-'*len(s) for s in col_name]
        store_table.writeLine(col_name)
        store_table.writeLine(underline)

        i = 1
        selector = []
        for product_row in product_detail:
            product_row = list(product_row)
            sid = product_row[-1]
            norders = orders_d[sid] if sid in orders_d else 0
            store_name, price, qty, sid = product_row[3:]
            row = [i, store_name, price, qty, norders]
            selector.append(sid)
            store_table.writeLine([str(s) for s in row])
            i += 1


        while True:
            clear_screen()
            print(detail_table)
            print('\nAvailable in the following stores:\n')
            print(store_table)
            print('What would you like to do next?')
            print('1. Add to cart')
            print('2. Go back')
            option = input('> ')
            clear_screen()
            if option == '1':
                while True:
                    print(detail_table)
                    print('\nAvailable in the following stores:\n')
                    print(store_table)
                    print('Please select the from the above list (type nothing to give up):')
                    selection = input('> ')
                    if selection == '':
                        break
                    elif int(selection) > 0 and int(selection) <= len(selector):
                        self.add_to_cart(pid, selector[int(selection)-1])
                        break
            elif option == '2':
                return

    def add_to_cart(self, pid, sid):
        for cart_pid, cart_sid, _ in self.cart:
            if cart_pid == pid and cart_sid == sid:
                clear_screen()
                print('This item already in your cart.')
                print('1. Go back')
                while True:
                    option = input('> ')
                    if option == '1':
                        return
        while True:
            print('How many units would you want to buy? (default: 1)')
            option = input('> ')
            if option == '':
                qty = 1
                break
            elif option.isdigit():
                qty = int(option)
                break
            elif option == '0':
                print('Cancelled.')
                print('1. Go back')
                while True:
                    option = input('> ')
                    if option == '1':
                        return
            else:
                print('Input error, you should type a number.')

        self.cart.append([pid, sid, qty])
        clear_screen()
        print('Item(s) added successfully.')
        print('1. Go back')
        while True:
            option = input('> ')
            if option == '1':
                return

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
