import re
import time
import sqlite3
import random
import hashlib
from getpass import getpass


conn = sqlite3.connect("customers_details.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS customers_details (
    account_number INTEGER PRIMARY KEY UNIQUE,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    balance REAL NOT NULL DEFAULT 0,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number INTEGER NOT NULL,
    username TEXT NOT NULL,                
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY(account_number) REFERENCES customers_details(account_number)
)
""")


def sign_up():

    print("******* Welcome to the Sign Up page ***************")
    
    while True:

        first_name = input("Enter your first name: ").strip()

        if not first_name:
            print("First name field cannot be left blank")
            continue

        if len(first_name) < 4 or len(first_name) > 255:
            print("Name must be between 4 and 255 characters.")
            continue

        valid_name = re.match(r"^[A-Za-z ]+$", first_name)
        if not valid_name:
            print("Name should only contains alphabetic characters")
            continue

        break

    while True:
        last_name = input("Enter your last name: ").strip()

        if not last_name:
            print("Last name field cannot be left blank")
            continue

        if len(last_name) < 4 or len(last_name) > 255:
            print("Name must be between 4 and 255 characters.")
            continue

        valid_name = re.match(r"^[A-Za-z ]+$", last_name)
        if not valid_name:
            print("Name should only contains alphabetic characters")
            continue

        break
    
    full_name = first_name + " " + last_name

    while True:
        username = input("Enter your username: ").strip()
        if not username:
            print("Last name field cannot be left blank")
            continue

        if len(username) < 3 or len(username) > 20:
            print("Name must be between 3 and 20 characters.")
            continue

        valid_username = re.match(r"^[A-Za-z0-9_]+$", username)
        if not valid_username:
            print("Name should only contains alphanumeric characters and undersores")
            continue

        break

    while True:

        try:
            initial_deposit = int(input("Enter your first deposit to your account: "))
        except ValueError:
            print("deposit must be a number")

        if initial_deposit < 2000:
            print("The minimum deposit is #2000 ")
            continue
        
        else:
            break

    while True:

        password = getpass("Enter your password: ").strip()
        if not password:
            print("Password field cannot be left blank")
            continue

        if len(password) < 8:
            print("Password too short - must be greater than 8 characters")
            continue

        valid_password  = re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", password)
        if not valid_password:
            print("password should contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
            continue

        confirm_password = getpass("Confirm your password: ").strip()
        if not confirm_password:
            print("Confirm Password field cannot be left blank")
            continue

        if password != confirm_password:
            print("passwords don't match")
            continue

        break

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    account_number = random.randrange(1000000000, 9999999999)


    try:
        cursor.execute("""
        INSERT INTO customers_details (account_number, full_name, username, balance, password) VALUES
        (?, ?, ?, ?, ?)
        """, (account_number, full_name, username, initial_deposit, hashed_password))
    except sqlite3.IntegrityError:
        print("Username already exists! please try another username")
    else:
        conn.commit()
        print("Congratulations!, your Sign Up was successful")
        print()
        print()
        log_in()



def log_in():
    print("********* Welcome to the Log In page ************")

    while True:
        username = input("Enter your username: ").strip()
        if not username:
            print("Last name field cannot be left blank")
            continue

        if len(username) < 3 or len(username) > 20:
            print("Name must be between 3 and 20 characters.")
            continue

        valid_username = re.match(r"^[A-Za-z0-9_]+$", username)
        if not valid_username:
            print("Name should only contains alphanumeric characters and undersores")
            continue

        break

    while True:
        password = getpass("Enter your password: ").strip()
        if not password:
            print("Password field cannot be left blank")
            continue

        if len(password) < 8:
            print("Password too short - must be greater than 8 characters")
            continue

        valid_password  = re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", password)
        if not valid_password:
            print("password should contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
            continue

        break


    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = cursor.execute("""
    SELECT account_number, full_name, username, balance FROM customers_details WHERE username = ? AND password = ?
""", (username, hashed_password)).fetchone()


    if user is None:
        print("Invalid username or password: ")
        return
    
    print()
    print("Log In Successful")
    print()
    time.sleep(3)
    menu(user)
    

def menu(user):
    while True:
        print(f"Welcome to your banking page '{user[1]}({user[0]})'")
        operation_menu(user)
        break
    

def deposit(user):

    try:
        deposit_amount = int(input("Enter the amount you want to deposit in figure: "))
        
        if deposit_amount <= 0:
            print("Deposit amount must be greater than zero.")
            return 
        
    except ValueError as e:
        print("Invalid input! Please enter a numeric amount.")
        return
    
    else:
        current_balance = deposit_amount + user[3]
        
        cursor.execute("""
        UPDATE customers_details
        SET balance = ?
        WHERE username = ?
""", (current_balance, user[2]))
        conn.commit()
        time.sleep(3)
    print()
    print(f"Deposit successful! Your new balance is: {current_balance}")
    print()

    cursor.execute("""
    INSERT INTO transactions (username, account_number, transaction_type, amount, date) VALUES
    (?, ?, ?, ?, CURRENT_TIMESTAMP)
""", (user[2], user[0], "Deposit", deposit_amount))
    conn.commit()
        

def withdrawal(user):

    try:
        withdrawal_amount = int(input("Enter the amount you want to withdraw in figure: "))
        
        if withdrawal_amount <= 0:
            print("withdrawal amount must be greater than zero.")
            return
        
        if withdrawal_amount > user[3]:
            print("Insufficient Balance!")
            return
        
    except ValueError as e:
        print("Invalid input! Please enter a numeric amount.")
        return
    
    else:
        new_balance = user[3] - withdrawal_amount
        
        cursor.execute("""
        UPDATE customers_details
        SET balance = ?
        WHERE username = ?
""", (new_balance, user[2]))
        conn.commit()
        time.sleep(3)

    print()
    print(f"Withdrawal successful! Your new balance is: {new_balance}")
    print()

    cursor.execute("""
    INSERT INTO transactions (username, account_number, transaction_type, amount, date) VALUES
    (?, ?, ?, ?, CURRENT_TIMESTAMP)
""", (user[2], user[0], "Withdrawal", withdrawal_amount))
    conn.commit()


def account_balance (user):
    acct_balance = cursor.execute("""
        SELECT balance FROM customers_details WHERE account_number = ?
    """, (user[0],)).fetchall()

    for balance_view in acct_balance:
        time.sleep(3)
        print(f"Your current account balance is {balance_view}")
        break



def transfer(user):
    while True:
        recipent_input = input("Enter the recipient account number: ").strip()
        if not recipent_input.isdigit():
            print("Please enter a valid numeric account number.")
            continue

        recipent_acct = int(recipent_input)

        if recipent_acct == user[0]:
            print("You cannot transfer money to your own account.")
            continue

        if len(str(recipent_acct)) < 10:
            print("You entered an incomplete account number.")
            continue

        recepient_exist = cursor.execute("""
            SELECT account_number, full_name, balance, username 
            FROM customers_details 
            WHERE account_number = ?
        """, (recipent_acct,)).fetchone()

        if not recepient_exist:
            print("Account number not found. Please enter a valid account number.")
            continue

        recepient_name = recepient_exist[1]
        print(f"Account found: '{recepient_name}'")
        break
    
    try:
        transfer_amount = int(input("Enter the amount you want to transfer in figure: "))
        
        if transfer_amount <= 0:
            print("Transfer amount must be greater than zero.")
            return 
        
        if transfer_amount > user[3]:
            print(f"Insufficient balance to transfer! You have '{user[3]}' only.")
            return
        
    except ValueError:
        print("Invalid input! Please enter a numeric amount.")
        return
    
    else:
        transfer_balance = user[3] - transfer_amount
        cursor.execute("""
            UPDATE customers_details
            SET balance = ?
            WHERE username = ?
        """, (transfer_balance, user[2]))
        conn.commit()
        time.sleep(3)
    
    print()
    print(f"Transfer successful! Your new balance is: {transfer_balance}")
    print()

    recepient_balance = recepient_exist[2] + transfer_amount
    cursor.execute("""
        UPDATE customers_details
        SET balance = ?
        WHERE account_number = ?
    """, (recepient_balance, recepient_exist[0]))
    conn.commit()
    
    cursor.execute("""
        INSERT INTO transactions (username, account_number, transaction_type, amount, date) 
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (user[2], user[0], "Transfer", transfer_amount))
    conn.commit()

    cursor.execute("""
        INSERT INTO transactions (username, account_number, transaction_type, amount, date) 
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (recepient_exist[3], recepient_exist[0], "Received Transfer", transfer_amount))
    conn.commit()




def view_transaction_history(user):
    transactions = cursor.execute("""
        SELECT * FROM transactions WHERE account_number = ?
    """, (user[0],)).fetchall()

    if not transactions:
        print("No transaction history found.")
        return
    
    print()
    time.sleep(3)
    print("************* Transaction History ***************")
    for idx, transaction in enumerate(transactions, start=1):
        print()
        print(f"{idx} {transaction}")

def operation_menu(user):
    while True:
        print("""
*************** Operation Menu ***************
Which operation do you wish to perform?

1. Deposit.
2. Withdrawal.
3. Tranfer
4. Account Balance
5. Transaction History
6. Quit
              
""")
        
        choice = input("Choose an option from the menu above: ").strip()

        if choice == "6":
            print("Thanks for banking with us!")
            break

        if choice == "1":
            deposit(user)

        elif choice == "2":
            withdrawal(user)

        elif choice == "3":
            transfer(user)
        
        elif choice == "4":
            account_balance(user)

        elif choice == "5":
            view_transaction_history(user)

        else:
            print("Invalid choice, select from the menu")


main_menu = """
***************Main Menu***************
1. Sign Up.
2. Log In
3. Quit

"""



try:
    while True:
        print(main_menu)
        choice = input("Choose an option from the menu above: ").strip()

        if choice == "3":
            print("Thanks for banking with us!")
            break

        if choice == "1":
            sign_up()

        elif choice == "2":
            log_in()
        else:
            print("Invalid choice, select from the menu")

except Exception as e:
    print(f"Oops! Something went wrong: {e}")
finally:
    conn.close()

