import sqlite3, time, os, getpass
from loginClass import *
os.system('clear')

def main():
        
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
        customer_login()
        

    elif acc_type == 'agent':
        agent_login()


def customer():
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
        login(failed_attempt)

    else:
        account_create()
        
def login_customer(failed_attempt):
    failed = failed_attempt
    if failed_attempt == 5:
        print('Too many failed attempts. GoodBye')
        return
    cid = input('Username: ')
    pwd = getpass.getpass('Password(hidden):')
    validate = Customer()
    valid_bool = validate.validate_session(cid,pwd)
    if valid_bool == True:
        customer_session = Customer_Session()
        customer_session.start_session(cid)
        customer_session.close()
    else:
        print('Username or Password was Incorrect')
        failed += 1
        login(failed)

def account_create():

    create_account = Customer()
    
    pwd = None
    print('Please Enter The Following Information')
    cid       = input('Username: ')
        
    firstName = input('First Name: ')
    lastName  = input('Last Name: ')
    name      = firstName + lastName
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
        account_create()
    else:
        
        return
            

def agent_login():
    aid = input('Username: ')
    pwd = getpass.getpass('Password(hidden):')




if __name__ == '__main__':
    main()



