import sqlite3
import sys
import datetime


connection = None
cursor = None

class Agent_Session:
    #---------------------------------------------------------------
    # Function Name : SetUpDelivery
    # Description: Given a trackingNumber by system, the program is 
    # responsible to add orders to the delivery as well as the pickup time 
    # 
    #---------------------------------------------------------------      

    def __init__(self):
        self.aid = None
        self.connection = sqlite3.connect('./database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('PRAGMA foreign_keys=ON;')


    def start_session(self, aid):
        '''Called from login interface'''
        self.aid = aid
        clear_screen()
        print('Agent Session Started.')
        trackingNumber_list = list(range(1000000, 9999999))

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


    def place_a_delivery(self):
        try:
            oid = int(raw_input('Please input the order number:'))
        except ValueError:
            print ('Order number not Valid')

        print ('Do you want a pick up time?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            pickUpTime = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            pickUpTime = None

        dropOffTime = None
        trackingno = trackingNumber_list[0]
        data = (trackingno, oid, pickUpTime, dropOffTime)
        cursor.execute('INSERT INTO deliveries VALUES (?,?,?,?);', data) 
        trackingNumber_list.pop(0)
        self.connection.commit()
        print('End setting up this delivery')
        '''query1 = ('UPDATE deliveries SET pickUpTime=? where oid=?;',self.pickUpTime, self.oid)
                    query2 = ('UPDATE deliveries SET dropOffTime=? where oid=?;',self.dropOffTime, self.oid)
                    self.cursor.execute(query1)
                    self.cursor.execute(query2)'''

    '''    print ('Do you want a drop off time?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            try:
                dropOffTime = str(raw_input('Please input the drop off time:'))
            except ValueError:
                print 'Drop off time not Valid'
        pass'''

    def update_delivery(self):
        print('Please input the tracking number below to select a delivery:')
        try:
            trackingno_current = int(raw_input('Tracking number: '))
        except ValueError:
            print ('Tracking number not Valid')

        self.cursor.execute('SELECT * FROM deliveries WHERE trackingno=?;', trackingno_current)
        print (self.cursor.fetchall()) # print the detail of selected delivery

        self.cursor.execute('SELECT o.* FROM orders o, deliveries d WHERE o.oid = d.oid and d.trackingno=?;', trackingno_current)
        print (self.cursor.fetchall())

        '''Update pick up time'''
        self.cursor.execute('SELECT pickUpTime FROM deliveries WHERE trackingno=?;', trackingno_current)
        pickUpTime_current = self.cursor.fetchone()

        if(pickUpTime_current == None):
            print ('Do you want to pick up this order?')
            choice = input(' Please input Y(yes) / N(no):  ')
            if(choice == 'Y' or choice == 'y'):
                    pickUpTime_current = time.strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute('UPDATE deliveries SET pickUpTime=? WHERE trackingno=?;',pickUpTime_current, trackingno_current)
        

        '''update drop off time'''
        self.cursor.execute('SELECT dropOffTime FROM deliveries WHERE trackingno=?;', trackingno_current)
        dropOffTime_current = self.cursor.fetchone()
        if(dropOffTime_current == None):
            print ('Do you want to drop off this order?')
            choice = input(' Please input Y(yes) / N(no):  ')
            if(choice == 'Y' or choice == 'y'):
                    dropOffTime = time.strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute('UPDATE deliveries SET dropOffTime=? WHERE trackingno=?;',dropOffTime_current, trackingno_current)
        
        '''Remove an order from the delivery'''
        print ('Do you want a drop off this order from deliveries?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            self.cursor.execute('DELETE from deliveries WHERE trackingno=?;', trackingno_current)

        print('End updating this delivery')

    def add_to_stock(self):
        print('Please input the (product id) and (store id) below to add to stock:')

        try:
            pid_current = int(raw_input('Product id: '))
        except ValueError:
            print ('Product id not Valid')

        try:
            sid_current = int(raw_input('Store id: '))
        except ValueError:
            print ('Store id not Valid')

        try:
            qty_current = int(raw_input('Please input the number of products to be added to the stock: '))
        except ValueError:
            print ('Number is not Valid')

        print ('Do you want to change the unit price for this product in stock?')
        choice = input(' Please input Y(yes) / N(no):  ')
        if(choice == 'Y' or choice == 'y'):
            try:
                uprice_current = int(raw_input('Please input the new price:'))
            except ValueError:
                print ('Input is not Valid')

        carry_current = (sid_current, pid_current, qty_current, uprice_current)
        self.cursor.execute('INSERT INTO carries VALUES (?,?,?,?);', carry_current)
        print('End adding to stock')

    def close(self):
            """
            Call this function at the end of the program.
            """
            self.connection.commit()
            self.connection.close()

def test():
    agent_session = Agent_Session()
    agent_session.start_session()
    agent_session.close()

if __name__ == '__main__':
    test()





