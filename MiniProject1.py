#!/usr/bin/env python3
import sqlite3, time, os, getpass, sys

from customer import *
from Agent import *
from loginClass import *
from agentLoginClass import *
os.system('clear')

#######################################################################
#   Main Function: Combines all Functions and Classes to create program
#######################################################################

def main():

    try:
        database = sys.argv[1]                      #stores database filename into variable
    except IndexError:                              #sends error message if db file is missing
        print('Missing Database File')
        return
    
    if database[-2:] != 'db':                       #makes sure that the db file is of correct filetype
    	print('Invalid File Type')
    	return

    print('Welcome. What would you like to do?')
    print('1. Login as Agent')
    print('2. Login as Customer')
    print('3. Exit')

    
        
    acc_type = input('> ') #User chooses wether they are logging in as agent or customer or to exit
    
    ##########################################################################
    # Loop checks if User entered appropriate response i.e Agent or Customer
    ##########################################################################
    while acc_type != '1' and acc_type != '2':
   
        if acc_type != '3':
            
            os.system('clear')
            print('Welcome. What would you like to do?')
            print('1. Login as Agent')
            print('2. Login as Customer')
            print('3. Exit')
            print('Invalid Login Type')
            acc_type = input('> ')
        else:
            os.system('clear')
            return

    os.system('clear')                             #clears the terminal in preperation for login screens
    
    if acc_type == '2':                      #transitions to customer login screen
        customer(database)                          #database parameter is the filename for the database
        

    elif acc_type == '1':                       #transitions to to agent screen
        failed_attempt = 0                          #initializes variable for use for max login attempts
        agent_login(failed_attempt,database)        #parameters are amount of failed login attempts and db filename

#################################################################
# Function for customer slection screen
# Allows users to either creat account or login to existing account
#################################################################

def customer(database):                            
    db = database                           #saves db filename into new variable as to not lose it
    print('What would you like to do?')     
    print('1. Login with existing account')
    print('2. Create Customer Account')
    
    # Loop to error check users answer, limiting it to only 1 or 2
    while True:
        try:
            cus_choice = int(input('> '))
            if cus_choice == 1 or cus_choice == 2:
                break
            else:
                print('Not a Valid Choice')
                                        
        except ValueError :
            print('Not A Number')
            
    os.system('clear')                              #clears terminal in preperation for login screen or account creation
    
    if cus_choice == 1:                              
        failed_attempt = 0
        login_customer(failed_attempt, db)          #customer login

    else:
        account_create(db)                          #account creation

##############################################################        
# Function used to login user to database then transfers user to 
# the Customer page for further interaction with db
##############################################################
def login_customer(failed_attempt, database):
    failed = failed_attempt
    if failed_attempt == 5:                         #checks if there were too many login attempts i.e 5
        print('Too many failed attempts. GoodBye')
        return
    cid = input('Username: ')                       #receives cid from user
    pwd = getpass.getpass('Password(hidden):')      #receives password, hides userinput from view
    validate = Customer(database)                   #creates a customer object from Customer class
    valid_bool = validate.validate_session(cid,pwd) #returns a bool value to see if cid and pwd were correct
    if valid_bool == True:
        customer_session = Customer_Session(database)   #if the user credentials were correct, initializes Customer Session
        customer_session.start_session(cid)             #starts session
        customer_session.close()                        #closes session to ensure databse is no longer in use
        os.system('clear')
        main()
    else:
        print('Username or Password was Incorrect')
        failed += 1
        login_customer(failed, database)                #if password or username were incorrect, ask again and increase login attempts

########################################################################
# Account creation function, gathers users Username, first and last name
# of which are concatenated into a single string, an address and 
# two instances of a password. Since password is hidden, i used 
# two instances of the password to ensure use has entered their password
# correctly. From there it adds user to database then continues onto
# the customer selection screen.
########################################################################


def account_create(database):

    create_account = Customer(database)                 #initializes class that speaks to db
    
    pwd = None
    print('Please Enter The Following Information')
    cid       = input('Username: ')
        
    firstName = input('First Name: ')
    lastName  = input('Last Name: ')
    name      = firstName + ' ' + lastName                          #concatenates first and last name into single variable
    address   = input('Address: ')
    while True:
        pwd1      = getpass.getpass('Password: ')                   #first password entry
        pwd2      = getpass.getpass('Please Re-Enter Password: ')   #second password entry
        if pwd1 != pwd2:                                            #checks if pwd1 and pwd2 don't match, then gets them to reenter
            os.system('clear')
            print('PASSWORDS DID NOT MATCH')                        ####################################################################
            print('Username: '+cid)                                 #variables cid, firstname, lastname and address are printed in order
            print('First Name: '+firstName)                         # to maintain cleanliness and continuity
            print('Last Name: '+lastName)                           ####################################################################
            print('Address: '+address)
            continue
        else:
            pwd = pwd1                                              #if pwd1 and pwd2 match, sets pwd to pwd1
            break                                                   #breaks out of while loop
    
    check_fail = create_account.add_customer(cid,name,address,pwd)  #check_fail boolean to see if cid is already ued
    if check_fail == True:                                          #if cid i taken , gets user to re sign up
        print('cid already taken')
        time.sleep(2)
        account_create(database)
    else:
        print('Thanks for Creating an Account. Redirecting To Customer Selection Screen')       #re-direction message
        time.sleep(1)
        os.system('clear')
        customer(database)
        
###################################
# Function to validate agents login
###################################

def agent_login(failed_attempt, database):
    failed = failed_attempt
    validate = Agent(database)                  #intilializes Agent object
    Valid_bool = False
    aid = input('Username: ')                   #Gets users aid and pwd
    pwd = getpass.getpass('Password(hidden):')
    Valid_bool = validate.validate_agent(aid, pwd)  #validates that aid and pwd are correct
    ###############################################################################################################################
    # remainder of lines notifies user that their aid or pwd are incorrect, then lets them know that if they dont have an account
    # they should get in contact with System Admin to creat account
    ###############################################################################################################################
    if Valid_bool == False:          
        print('Username or Password was incorrect')
        print('If you do not have an account, please see System Admin or Login as Customer')
        failed += 1
        agent_login(failed, database)
        
    else:
        agent_session = Agent_Session(database)
        agent_session.start_session(aid)
        agent_session.close()
        os.system('clear')
        main()


if __name__ == '__main__':
    main()



