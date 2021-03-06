#!/usr/bin/env python3

import sqlite3
import re
from utils import *
from pretty_table import PrettyTable


class Customer_Session:
    def __init__(self, database):
        self.cid = None
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys=ON;')
        self.per_page = 5 # num of rows per page

    def start_session(self, cid):
        """
        Main interface, called from login system
        """
        self.cid = cid
        self.cart = []
        clear_screen()
        print ('Customer session started.')
        while True:
            print ('Welcome, what would you like to do today?')
            print ('1. Search for products')
            print ('2. Place an order')
            print ('3. List orders')
            print ('4. Logout')
            choice = input('> ')
            if choice == '1':
                self.search_for_products()
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

    def search_for_products(self):
        '''
        Main Function 1: Customer search for products
        '''
        display = Display()
        err_msg = False
        while True:
            clear_screen()
            print('Please enter keywords:')
            if err_msg:
                print('Error: illegal character found in keywords')
                err_msg = False
            search_input = input('> ')
            if search_input != '':
                keywords = search_input.strip().split() # split into list
                if not self.check_keyword(keywords):
                    err_msg = True
                    continue

                # Search keywords:
                product_detail, product_orders = self.sql_search_products(
                        keywords)

                # Divide sarch result into pages
                page_view = PageView(product_detail, self.per_page)
                while True:
                    table = PrettyTable(8) # create a table to show result
                    table.addLabel(['Product ID', 'Product Name', 'Unit',
                            'Num. of Stores Carry', 'Num. of Stores In Stock',
                            'Min. Price Carry', 'Min. Price In Stock',
                            'Num. of Orders Past 7 Days'])

                    # Product a table to show the result:
                    products = []
                    for row in page_view.get_view(): # show page start from 0
                        row = list(row)
                        pid = row[0]
                        norder = 0
                        for line in product_orders:
                            if line[0] == pid:
                                norder = line[1]
                        row.append(norder)
                        products.append(row)

                        # write row to table
                        table.writeLine([str(r) for r in row])
                    display.add(table)

                    display.show()
                    print('What would you like to do next?')
                    print('1. See product details')
                    print('2. Go back')
                    print('3. Next page')
                    print('4. Previous Page')
                    option = input('> ')
                    if option == '1':
                        available_pids = [str(p) for p in list(zip(*products))[0]]
                        while True:
                            display.show()
                            print('Please select a product ID (type nothing to go back):')
                            selection = input('> ')
                            if selection == '':
                                break
                            elif selection in available_pids:
                                self.see_product_details(selection)
                    elif option == '2':
                        break
                    elif option == '3':
                        page_view.next_page()
                    elif option == '4':
                        page_view.prev_page()
                    display.refresh()

                break

    def place_an_order(self):
        '''
        Main Function 2: Customer Placing Order
        '''
        display = Display()

        # Cart is empty:
        if len(self.cart) == 0:
            display.add('Your cart is empty.')
            display.show()
            while True:
                print('1. Go back')
                option = input('> ')
                if option == '1':
                    return
        else:
            # Check if the quantity is too large, update new quantities to
            # new_cart.
            new_cart = []
            for pid, sid, product_name, store_name, price, qty in self.cart:

                # Check quantity for given product:
                self.cursor.execute(
                        '''
                        SELECT qty FROM carries
                        WHERE sid = ?
                            AND pid = ?;
                        ''',
                        (sid, pid)
                )
                qty_left = self.cursor.fetchall()[0][0]

                # Not enough quantity, ask user to reduct order quantity:
                while qty > qty_left:
                    display.add(
                            'The following item(s) cannot be ordered:'
                    )
                    display.add(
                            '{} from {}'.format(product_name, store_name)
                    )
                    display.add(
                            'You have added {} item(s), but there is only {} left. Please adjust the quantity.'.format(qty, qty_left)
                    )
                    display.show()
                    raw_qty = input('> ')
                    if raw_qty.isdigit():
                        qty = int(raw_qty)
                if qty > 0:
                    new_cart.append([pid, sid, product_name, store_name, price, qty])

            self.cart = new_cart # update cart

            # If nothing left in cart:
            if len(self.cart) == 0:
                display.refresh()
                display.add('Your cart is emtpy.')
                display.add('1. Go back')
                while True:
                    display.show()
                    option = input('> ')
                    if option == '1':
                        return

            # Looking for confirm order:
            display.refresh()
            display.add(
                    'Looks good! Please confirm your order:'
            )

            # Generate a summary table:
            summary = PrettyTable(4)
            summary.addLabel(['Product Name', 'Store', 'Quantity', 'Subtotal'])
            total = 0.0
            for cart_item in self.cart:
                pid, sid, product_name, store_name, price, qty = cart_item
                subtotal = float(qty) * float(price)
                total += subtotal
                summary.writeLine([product_name, store_name, str(qty), str(subtotal)])
            display.add(summary)

            display.add('Total: {}'.format(total))
            display.add('1. Confirm')
            display.add('2. Go back')
            while True:
                display.show()
                option = input('> ')
                if option == '1':
                    # Get customer address:
                    self.cursor.execute(
                            '''
                            SELECT address FROM customers
                            WHERE cid = ?;
                            ''',
                            (self.cid, )
                    )
                    addr = self.cursor.fetchall()[0][0]

                    # Generate new oid:
                    self.cursor.execute(
                            '''
                            SELECT MAX(oid) FROM orders;
                            '''
                    )
                    max_oid = self.cursor.fetchall()[0][0]
                    if max_oid is None:
                        max_oid = 0
                    oid = max_oid + 1

                    # Update product qty from stores:
                    for pid, sid, product_name, store_name, price, qty in self.cart:
                        self.cursor.execute(
                                '''
                                SELECT qty FROM carries
                                WHERE sid = ?
                                    AND pid = ?;
                                ''',
                                (sid, pid)
                        )
                        qty_left = self.cursor.fetchall()[0][0]
                        self.cursor.execute(
                                '''
                                UPDATE carries
                                SET qty = ?
                                WHERE sid = ?
                                    AND pid = ?;
                                ''',
                                (qty_left - qty, sid, pid)
                        )
                    self.connection.commit()

                    # Insert new entry to orders table:
                    self.cursor.execute(
                            '''
                            INSERT INTO orders VALUES (?, ?, DATE(\'now\'), ?);
                            ''',
                            (oid, self.cid, addr)
                    )

                    # Insert new entries to olines table:
                    for cart_item in self.cart:
                        pid, sid, product_name, store_name, price, qty = cart_item
                        self.cursor.execute(
                                '''
                                INSERT INTO olines VALUES (?, ?, ?, ?, ?);
                                ''',
                                (oid, sid, pid, qty, price)
                        )

                    self.connection.commit()
                    self.cart = []
                    display.refresh()
                    display.add('Thank you, your order has been placed!')
                    display.add('1. Go back')
                    while True:
                        display.show()
                        option = input('> ')
                        if option == '1':
                            return

                elif option == '2':
                    return

    def list_orders(self):
        '''
        Main Function 3: List user orders
        '''
        display = Display()

        # Get all orders for given customer:
        self.cursor.execute(
                '''
                --SELECT orders.oid, odate, COUNT(pid), SUM(uprice * qty)
                SELECT orders.oid, odate, SUM(qty), SUM(uprice * qty)
                FROM orders, olines
                WHERE orders.oid = olines.oid
                    AND cid = ?
                GROUP BY orders.oid
                ORDER BY odate DESC;
                ''',
                (self.cid, )
                )
        orders = self.cursor.fetchall()

        # The order is already sorted by date, now we want to additionally
        # sort by reversed oid so the most recent order within the same day
        # comes first.
        orders = sorted(orders, key=lambda x: x[0], reverse=True) 

        # Divide orders into pages:
        page_view = PageView(orders, self.per_page)

        # No order found:
        if len(orders) == 0:
            display.add('You don\'t have any order.')
            display.add('1. Go back')
            while True:
                display.show()
                if input('> ') == '1':
                    return

        # Show orders:
        else:
            while True:
                table = PrettyTable(4)
                table.addLabel(['Order ID', 'Order Date', 'Num. of Products', 'Total Price'])
                valid_oids = []
                for each in page_view.get_view():
                    valid_oids.append(str(each[0]))
                    table.writeLine([str(s) for s in each])
                display.add(table)
                display.add('What would you like to do?')
                display.add('1. See order detail')
                display.add('2. Go back')
                display.add('3. Next page')
                display.add('4. Previous page')
                display.show()
                option = input('> ')
                if option == '1':
                    self.see_order_detail(valid_oids, display)
                elif option == '2':
                    return
                elif option == '3':
                    page_view.next_page()
                elif option == '4':
                    page_view.prev_page()
                display.refresh()

    def check_keyword(self, keywords):
        '''
        Check if keywords contain illegal characters:
        '''
        for kwd in keywords:
            if not re.match('^[A-Za-z0-9_-]*$', kwd):
                return False
        return True

    def sql_search_products(self, keywords):
        '''
        SQL search product matching given keywords.
        '''
        # Search for products contain given keywords, order by number of
        # matches, create a view for later operations.
        self.cursor.execute(
                'CREATE VIEW search_result AS ' + \
                'SELECT pid, name, unit, COUNT(name) FROM ( ' + \
                ' UNION ALL '.join(
                    'SELECT * FROM products WHERE name LIKE \'%{}%\''.format(kwd) \
                    for kwd in keywords
                ) + \
                ') GROUP BY name ORDER BY COUNT(name) DESC;'
        )
        
        # Given search result, check availability in stores:
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

        # Given search result, check how many orders in the last 7 days:
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

        # Delete the view:
        self.cursor.execute(
                '''
                DROP VIEW search_result;
                '''
        )
        return product_detail, product_orders

    def see_product_details(self, pid):
        '''
        Helper function, get more detail of given product.
        '''
        # Find stores information of a product, price, quantities, etc.
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

        # Find how many orders in the past 7 days for each store:
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
        orders_d = {} # put this into a dictionary for easier use
        for sid, norder in orders:
            orders_d[sid] = norder

        # Show product detail:
        display = Display()
        detail_table = PrettyTable(4)
        detail_table.addLabel(['Product ID', 'Product Name', 'Unit', 'Category'])
        detail_table.writeLine([str(pid)] + [str(s) for s in list(product_detail[0])[:3]])

        display.add(detail_table)
        display.add('\nAvailable in the following stores:\n')

        # Show stores information in a table:
        store_table = PrettyTable(5)
        store_table.addLabel(['Select', 'Store', 'Price', 'Quantities Left',
                 'Num. of Orders in 7 days'])
        i = 1
        selector = []
        for product_row in product_detail:
            product_row = list(product_row)
            sid = product_row[-1]
            norders = orders_d[sid] if sid in orders_d else 0
            store_name, price, qty, sid = product_row[3:]
            row = [i, store_name, price, qty, norders]
            selector.append([sid, store_name, price])
            store_table.writeLine([str(s) for s in row])
            i += 1
        display.add(store_table)

        while True:
            display.show()
            print('What would you like to do next?')
            print('1. Add to cart')
            print('2. Go back')
            option = input('> ')
            if option == '1':
                while True:
                    display.show()
                    print('Please select the from the above list (type nothing to give up):')
                    selection = input('> ')
                    if selection == '':
                        break
                    elif selection.isdigit():
                        if int(selection) > 0 and int(selection) <= len(selector):
                            # Selected a valid product in valid store:
                            sid, store_name, price = selector[int(selection) - 1]
                            product_name = product_detail[0][0]
                            self.add_to_cart(pid, sid, product_name, store_name, price, display)
                            break
            elif option == '2':
                return

    def add_to_cart(self, pid, sid, product_name, store_name, price, parent_display):
        '''
        Helper function, add product to customer cart for later placing order.
        '''
        display = Display()

        # If the item is already in the cart:
        for cart_item in self.cart:
            cart_pid, cart_sid = cart_item[:2]
            if cart_pid == pid and cart_sid == sid:
                display.add('This item already in your cart.')
                display.show()
                print('1. Go back')
                while True:
                    option = input('> ')
                    if option == '1':
                        return

        # Ask for quantity:
        while True:
            parent_display.show()
            print('How many units would you want to buy? (default: 1)')
            option = input('> ')
            if option == '':
                qty = 1
                break
            elif option.isdigit():
                qty = int(option)
                if qty == 0:
                    display.add('Cancelled.')
                    display.show()
                    print('1. Go back')
                    while True:
                        option = input('> ')
                        if option == '1':
                            return
                break

        # Add to cart:
        self.cart.append([pid, sid, product_name, store_name, price, qty])
        display.refresh()
        display.add('Item(s) added successfully.')
        display.show()
        print('1. Go back')
        while True:
            option = input('> ')
            if option == '1':
                return

    def see_order_detail(self, valid_oids, parent_display):
        '''
        Helper Function, get more detail of user selected order.
        '''
        display = Display()
        while True:
            parent_display.show()
            print('Please type the Order ID:')
            typed_oid = input('> ')
            if typed_oid in valid_oids:
                display.refresh()
                oid = int(typed_oid)

                # Get delivery info of given oid:
                self.cursor.execute(
                        '''
                        SELECT trackingNo, pickUpTime, dropOffTime
                        FROM deliveries
                        WHERE oid = ?;
                        ''',
                        (oid, )
                )
                deliveries = self.cursor.fetchall()

                # Get address of order:
                self.cursor.execute(
                        '''
                        SELECT address
                        FROM orders
                        WHERE oid = ?;
                        ''',
                        (oid, )
                )
                address = self.cursor.fetchall()[0][0]

                # Get detail of each product in the order:
                self.cursor.execute(
                        '''
                        SELECT olines.sid, stores.name, olines.pid,
                            products.name, olines.qty,
                            products.unit, olines.uprice
                        FROM olines, stores, products
                        WHERE olines.oid = ?
                            AND olines.sid = stores.sid
                            AND olines.pid = products.pid;
                        ''',
                        (oid, )
                )
                details = self.cursor.fetchall()

                # Show order detail:
                order_detail = PrettyTable(4)
                order_detail.addLabel(['Tracking Number', 'Pickup Time',
                        'Dropoff Time', 'Address'])
                if len(deliveries) == 0:
                    order_detail.writeLine(
                            ['N/A', 'N/A', 'N/A', address]
                    )
                else:
                    order_detail.writeLine(
                            [str(s) for s in list(deliveries[0])] + [address]
                    )
                display.add(order_detail)

                # Show product detail:
                product_table = PrettyTable(7)
                product_table.addLabel(['Store ID', 'Store Name', 'Product ID',
                        'Product Name', 'Quantity', 'Unit', 'Price'])
                for line in details:
                    product_table.writeLine(
                            [str(s) for s in line]
                    )
                display.add(product_table)

                while True:
                    display.show()
                    print('1. Go back')
                    if input('> ') == '1':
                        return

    def close(self):
        """
        Call this function at the end of the program.
        """
        self.connection.commit()
        self.connection.close()

def test():
    customer_session = Customer_Session('./database.db')
    customer_session.start_session('c01')
    customer_session.close()

if __name__ == '__main__':
    test()
