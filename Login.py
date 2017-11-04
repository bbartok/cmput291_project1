import sqlite3, time, os, getpass, sys
from loginClass import *
from agentLoginClass import *
os.system('clear')

def main():

    try:
        database = sys.argv[1]
        testconnection = sqlite3.connect(database)
        testconnection.close()
    except IndexError:
        print('Missing Database File')
        return
    
    if database[-2:] != 'db':
    	print('Invalid File Type')
    	return
    
        
    acc_type = input('Agent or Customer: ').lower()
    
    while acc_type != 'agent' and acc_type != 'customer':
   
        if acc_type != 'exit':
            print('Invalid Login Type')
            time.sleep(1.2)
            os.system('clear')
            acc_type = input('Agent or Customer: ').lower()
        else:
            return

    os.system('clear')
    
    if acc_type == 'customer':
        customer(database)
        

    elif acc_type == 'agent':
        failed_attempt = 0
        agent_login(failed_attempt,database)


def customer(database):
    db = database
    print('What would you like to do?')
    print('1. Login with existing account')
    print('2. Create Customer Account')
        
    while True:
        try:
            cus_choice = int(input('> '))
            if cus_choice == 1 or cus_choice == 2:
                break
            else:
                print('Not a Valid Choice')
                                        
        except ValueError :
            print('Not A Number')
            
    os.system('clear')
    
    if cus_choice == 1:
        failed_attempt = 0
        login_customer(failed_attempt, db)

    else:
        account_create(db)
        
def login_customer(failed_attempt, database):
    failed = failed_attempt
    if failed_attempt == 5:
        print('Too many failed attempts. GoodBye')
        return
    cid = input('Username: ')
    pwd = getpass.getpass('Password(hidden):')
    validate = Customer(database)
    valid_bool = validate.validate_session(cid,pwd)
    if valid_bool == True:
        customer_session = Customer_session(database)
        customer_session.start_session(cid)
        customer_session.close()
    else:
        print('Username or Password was Incorrect')
        failed += 1
        login_customer(failed, database)

def account_create(database):

    create_account = Customer(database)
    
    pwd = None
    print('Please Enter The Following Information')
    cid       = input('Username: ')
        
    firstName = input('First Name: ')
    lastName  = input('Last Name: ')
    name      = firstName + ' ' + lastName
    address   = input('Address: ')
    while True:
        pwd1      = getpass.getpass('Password: ')
        pwd2      = getpass.getpass('Please Re-Enter Password: ')
        if pwd1 != pwd2:
            os.system('clear')
            print('PASSWORDS DID NOT MATCH')
            print('Username: '+cid)
            print('First Name: '+firstName)
            print('Last Name: '+lastName)
            print('Address: '+address)
            continue
        else:
            pwd = pwd1
            break  
    
    check_fail = create_account.add_customer(cid,name,address,pwd)
    if check_fail == True:
        print('cid already taken')
        time.sleep(2)
        account_create(database)
    else:
        print('Thanks for Creating an Account. Redirecting To Customer Selection Screen')
        time.sleep(1)
        os.system('clear')
        customer(database)
        
            

def agent_login(failed_attempt, database):
    failed = failed_attempt
    validate = Agent(database)
    Valid_bool = False
    aid = input('Username: ')
    pwd = getpass.getpass('Password(hidden):')
    Valid_bool = validate.validate_agent(aid, pwd)
    if Valid_bool == False:
        print('Username or Password was incorrect')
        print('If you do not have an account, please see System Admin or Login as Customer')
        failed += 1
        agent_login(failed, database)
    



if __name__ == '__main__':
    main()



