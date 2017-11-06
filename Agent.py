import sqlite3
import sys
import time
import datetime
import os


class Agent_Session:

    def __init__(self, database):
        self.aid = None
        # self.connection = sqlite3.connect('database.db')
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys=ON;')


    def start_session(self, aid):
        '''Called from login interface'''
        self.aid = aid
        clear_screen()
        print('Agent Session Started.')
        self.trackingNumber_list = list(map(int, range(1000000, 9999999)))

        while True:
            print ('Welcome, {}. What would you like to do today?'.format(aid))
            print ('1. Place a delivery')
            print ('2. Update a delivery')
            print ('3. Add to stock')
            print ('4. Logout')
            choice = input(' > ')
            if choice == '1':
                self.place_a_delivery()
            elif choice == '2':
                self.update_delivery()
            elif choice == '3':
                self.add_to_stock()
            elif choice == '4':
                print ('Logging you out, have a nice day!')
                self.aid = None
                print ('Customer session ended.')
                break
            clear_screen()

    #---------------------------------------------------------------
    # Function Name : place_a_delivery
    # Description: Given a trackingNumber by system, the program is 
    # responsible to add orders to the delivery as well as the pickup time 
    # 
    #---------------------------------------------------------------      


    def place_a_delivery(self):
        try:
            oid = int(input('Please input the order number:'))
        except ValueError:
            print ('Order number not Valid, will return to main menu after 1.2s')
            time.sleep(1.2)
            self.start_session('1234')

        self.cursor.execute('SELECT * FROM orders WHERE oid=?;', (oid,))
        temp = (self.cursor.fetchall())
        if (temp == []):
            print ('Order number not in the database, will return to main menu after 1.2s')
            time.sleep(1.2)
            self.start_session('1234')

        self.cursor.execute('SELECT * FROM deliveries WHERE oid=?;', (oid,))
        temp = (self.cursor.fetchall())
        if (temp != []):
            print ('Order number already has a delivery, will return to main menu after 1.2s')
            time.sleep(1.2)
            self.start_session('1234')

        print ('Do you want a pick up time in the future?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            try:
                d = int(input(' Please input Input the day ahead:  '))
            except ValueError:
                print ('Input value error, set day ahead to 0')
                d = 0

            try:
                h = int(input(' Please input Input the hour ahead:  '))
            except ValueError:
                print ('Input value error, set hour ahead to 0')
                h = 0

            try:
                m = int(input(' Please input Input the minute ahead:  '))
            except ValueError:
                print ('Input value error, set minute ahead to 0')
                m = 0
                            
            # pickUpTime = time.strftime("%Y-%m-%d %H:%M:%S", )
            day_temp = str(str(d) + ' days')
            hour_temp = str(str(h) + ' hours')
            minute_temp = str(str(m) + ' minutes')
            self.cursor.execute('select datetime(\'now\',?,?,?);',(day_temp, hour_temp, minute_temp))
            temp = (self.cursor.fetchone())
            temp = str(temp)
            pickUpTime = temp[2:-3]

            
        else:
            pickUpTime = None

        dropOffTime = None
        trackingno = self.trackingNumber_list[0]
        data = (trackingno, oid, pickUpTime, dropOffTime)
        self.cursor.execute('INSERT INTO deliveries VALUES (?,?,?,?);', data)        
        self.trackingNumber_list.pop(0)
        self.connection.commit()
        print('End setting up this delivery')
        time.sleep(1.2)
        self.start_session('1234')
        '''query1 = ('UPDATE deliveries SET pickUpTime=? where oid=?;',self.pickUpTime, self.oid)
                    query2 = ('UPDATE deliveries SET dropOffTime=? where oid=?;',self.dropOffTime, self.oid)
                    self.cursor.execute(query1)
                    self.cursor.execute(query2)'''

    '''    print ('Do you want a drop off time?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            try:
                dropOffTime = str(input('Please input the drop off time:'))
            except ValueError:
                print 'Drop off time not Valid'
        pass'''

    #---------------------------------------------------------------
    # Function Name : update_delivery
    # Description: Update a delivery. An agent should be able select 
    # a delivery using its tracking number and see its details including 
    # the orders being delivered. The agent should be able to pick up an 
    # order and update the pick up time and/or the drop off time. Also the 
    # agent should be able to remove an order from the delivery.
    #---------------------------------------------------------------      

    def update_delivery(self):
        print('Please input the tracking number below to select a delivery:')
        try:
            trackingno_current = int(input('Tracking number: '))
        except ValueError:
            print ('Tracking number not Valid, will return to main menu after 1.2s')
            time.sleep(1.2)
            self.start_session('1234')


        self.cursor.execute('SELECT trackingno from deliveries WHERE trackingno=?', (trackingno_current,))
        temp = (self.cursor.fetchall())
        if (temp == []):
            print ('Tracking number not in the database, will return to main menu after 1.2s')
            time.sleep(1.2)
            self.start_session('1234')

################################# Display information #########################################
        self.cursor.execute('SELECT * FROM deliveries WHERE trackingno=?;', (trackingno_current,))
        print ('Below are the detail of selected delivery')
        print('trackingno , oid,    pickUpTime    ,    dropOffTime    ')
        print (self.cursor.fetchall()) # print the detail of selected delivery

        print ('Below are the detail of related order')
        print('  oid  , cid  ,       odate      ,  address')
        self.cursor.execute('SELECT o.* FROM orders o, deliveries d WHERE o.oid = d.oid and d.trackingno=?;', (trackingno_current,))
        print (self.cursor.fetchall())

################################# Update pick up time ######################################
        self.cursor.execute('SELECT pickUpTime FROM deliveries WHERE trackingno=?;', (trackingno_current,))
        pickUpTime_current = self.cursor.fetchone()
        print(pickUpTime_current) ###
        if(pickUpTime_current == (None,)):
            print ('Do you want to pick up this order right now?')
            choice = input(' Please input Y(yes) / N(no):  ')
            if(choice == 'Y' or choice == 'y'):
                    pickUpTime_current = time.strftime("%Y-%m-%d %H:%M:%S")
                    data = (pickUpTime_current, trackingno_current)
                    self.cursor.execute('UPDATE deliveries SET pickUpTime=? WHERE trackingno=?;',data)
                    
        print ('Do you want update the pick up time for this order?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            try:
                d = int(input(' Please input Input the day ahead:  '))
            except ValueError:
                print ('Input value error, set day ahead to 0')
                d = 0

            try:
                h = int(input(' Please input Input the hour ahead:  '))
            except ValueError:
                print ('Input value error, set hour ahead to 0')
                h = 0

            try:
                m = int(input(' Please input Input the minute ahead:  '))
            except ValueError:
                print ('Input value error, set minute ahead to 0')
                m = 0
                            
            # pickUpTime = time.strftime("%Y-%m-%d %H:%M:%S", )
            day_temp = str(str(d) + ' days')
            hour_temp = str(str(h) + ' hours')
            minute_temp = str(str(m) + ' minutes')
            self.cursor.execute('select datetime(\'now\',?,?,?);',(day_temp, hour_temp, minute_temp))
            temp = (self.cursor.fetchone())
            temp = str(temp)
            pickUpTime_current = temp[2:-3]
            data = (pickUpTime_current, trackingno_current)
            self.cursor.execute('UPDATE deliveries SET pickUpTime=? WHERE trackingno=?;',data)

############################# update drop off time ##################################
        self.cursor.execute('SELECT dropOffTime FROM deliveries WHERE trackingno=?;', (trackingno_current,))
        dropOffTime_current = self.cursor.fetchone()
        print(dropOffTime_current) ###
        if(dropOffTime_current == (None,)):
            print ('Do you want a drop off time (now) for this order?')
            choice = input(' Please input Y(yes) / N(no):  ')
            if(choice == 'Y' or choice == 'y'):
                dropOffTime_current = time.strftime("%Y-%m-%d %H:%M:%S")
                print(dropOffTime_current)
                data = (dropOffTime_current, trackingno_current)
                self.cursor.execute('UPDATE deliveries SET dropOffTime=? WHERE trackingno=?;',data)
            else:
                print ('Do you want update the drop off time for this order (in the future)?')
                choice = input(' Please input Y(yes) / N(no):  ')
                if(choice == 'Y' or choice == 'y'):
                    try:
                        d = int(input(' Please input Input the day ahead:  '))
                    except ValueError:
                        print ('Input value error, set day ahead to 0')
                        d = 0

                    try:
                        h = int(input(' Please input Input the hour ahead:  '))
                    except ValueError:
                        print ('Input value error, set hour ahead to 0')
                        h = 0

                    try:
                        m = int(input(' Please input Input the minute ahead:  '))
                    except ValueError:
                        print ('Input value error, set minute ahead to 0')
                        m = 0
                                    
                    # pickUpTime = time.strftime("%Y-%m-%d %H:%M:%S", )
                    day_temp = str(str(d) + ' days')
                    hour_temp = str(str(h) + ' hours')
                    minute_temp = str(str(m) + ' minutes')
                    self.cursor.execute('select datetime(\'now\',?,?,?);',(day_temp, hour_temp, minute_temp))
                    temp = (self.cursor.fetchone())
                    temp = str(temp)
                    pickUpTime_current = temp[2:-3]
                    data = (dropOffTime_current, trackingno_current)
                    self.cursor.execute('UPDATE deliveries SET dropOffTime=? WHERE trackingno=?;',data)

############################ Remove an order from the delivery #################################
        print ('Do you want to drop off this order from deliveries?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            self.cursor.execute('DELETE from deliveries WHERE trackingno=?;', (trackingno_current,))

        print('End updating this delivery')
        time.sleep(1.2)
        self.start_session('1234')

    #---------------------------------------------------------------
    # Function Name : add_to_stock
    # Description: Add to stock. An agent should be able to select a 
    # product and a store (by giving the product id and the store id) 
    # and give the number of products to be added to the stock. The 
    # agent should have the option to change the unit price.
    #---------------------------------------------------------------      


    def add_to_stock(self):
        print('Please input the (product id) and (store id) below to add to stock:')
        while True:
            try:
                pid_current = str(input('Product id: '))
                break
            except ValueError:
                print ('Product id not Valid, try again')


        self.cursor.execute('SELECT * FROM products WHERE pid=?;', (pid_current,))
        temp = (self.cursor.fetchall())
        if (temp == []):
            print ('Product number not in the database, will return to main menu after 1.2s')
            time.sleep(1.2)
            self.start_session('1234')

        while True:
            try:
                sid_current = int(input('Store id: '))
                break
            except ValueError:
                print ('Store id not Valid, try again')

        self.cursor.execute('SELECT * FROM stores WHERE sid=?;', (sid_current,))
        temp = (self.cursor.fetchall())
        if (temp == []):
            print ('Store number not in the database, will return to main menu after 1.2s')
            time.sleep(1.2)
            self.start_session('1234')

        while True:
            try:
                qty_current = int(input('Please input the number of products to be added to the stock: '))
                break
            except ValueError:
                print ('Number is not Valid')

        print ('Do you want to change the unit price for this product in stock?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            while True:
                try:
                    uprice_current = float(input('Please input the new price:'))
                    uprice_current = '{0:%.2f}'.format(qty_current)
                    break
                except ValueError:
                    print ('Input is not Valid')
            carry_current = (sid_current, pid_current, qty_current, uprice_current)
            self.cursor.execute('INSERT INTO carries VALUES (?,?,?,?);', carry_current)

        else:
            carry_current = (sid_current, pid_current, qty_current)
            self.cursor.execute('INSERT INTO carries VALUES (?,?,?);', carry_current)
            print('End adding to stock')

    def close(self):
            """
            Call this function at the end of the program.
            """
            self.connection.commit()
            self.connection.close()

def test():
    agent_session = Agent_Session()
    agent_session.start_session('1234')
    agent_session.close()

def clear_screen():
    os.system('clear')

if __name__ == '__main__':
    test()





