class Account:
    def __init__(self,account_number,holder_name,balance = 0):
        self.account_number = account_number
        self.holder_name = holder_name
        self.balance = balance

    def deposit(self,amount):
            if amount > 0:
                self.balance += amount
                return True
            return False
        
    def withdraw(self,amount):
            if 0< amount <= self.balance:
                self.balance -= amount
                return True
            return False
        
    def transfer(self,target_account,amount):
            if self.withdraw(amount):
                target_account.deposit(amount)
                return True
            return False

    def display_info(self):
            return f"Account Number: {self.account_number} \nHolder Name: {self.holder_name}\nBalance: ${self.balance:.2f}"

class SavingsAccount(Account):
    def __init__(self,account_number,holder_name,balance = 0):
        super().__init__(account_number,holder_name,balance)
        self.interest_rate = 0.08

    def add_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest
    
    def display_info(self):
        base_info = super().display_info()
        return f"{base_info}\nAccount Type: Savings \nInterest Rate: {self.interest_rate*100}%"

class DepositAccount(Account):
    def __init__(self,account_number,holder_name,balance = 0):
        super().__init__(account_number,holder_name,balance)
        self.interest_rate = 0.07

    def add_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest
    
    def display_info(self):
        base_info = super().display_info()
        return f"{base_info}\nAccount Type: Deposit \nInterest Rate: {self.interest_rate*100}%"

class Bank:
    def __init__(self):
        self.accounts =[]

    def open_account(self,account_type,account_number,holder_name,initial_deposit=0):
        if not any (acc.account_number == account_number for acc in self.accounts):
            if account_type.lower() == 'savings':
                account = SavingsAccount(account_number,holder_name,initial_deposit)
            elif account_type.lower() == "deposit":
                account = DepositAccount(account_number,holder_name, initial_deposit)
            else:
                return None
            
            self.accounts.append(account)
            return account
        return None

    def close_account(self,account_number):
        account = self.find_account(account_number)
        if account:
            self.accounts.remove(account)
            return True
        return False

    def find_account(self,account_number):
        for account in self.accounts:
            if account.account_number == account_number:
                return account
        return None

    def transfer_funds(self,from_account_num,to_account_num,amount):
        from_account = self.find_account(from_account_num)
        to_account = self.find_account(to_account_num)

        if from_account and to_account:
            return from_account.transfer(to_account,amount)
        return False
    
    def add_interest_to_savings(self):
        total_interest =0
        for account in self.accounts:
            if isinstance(account,(SavingsAccount,DepositAccount)):
                interest = account.add_interest()
                total_interest += interest
        return total_interest

def bank_menu():
    bank = Bank()

    while True:
        print ("\n Bank Account Management System")
        print("1. Open Account")
        print("2. Close Account")
        print("3. Deposit Money")
        print("4. Withdraw Money")
        print("5. Transfer Funds")
        print("6. Display Account Info")
        print("7. Add Interest to Savings Accounts")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            account_type = input("Enter account type (savings/deposit): ")
            account_number = input("Enter account number: ")
            holder_name = input("Enter holder name: ")
            initial_deposit = float(input("Enter initial deposit (0 if none): ") or 0)

            account = bank.open_account(account_type, account_number, holder_name, initial_deposit)
            if account:
                print(f"Account created successfully!\n{account.display_info()}")
            else:
                print("Failed to create account. Account number may already exist.")

        elif choice == '2':
            account_number = input("Enter account number to close: ")
            if bank.close_account(account_number):
                print("Account closed successfully.")
            else:
                print("Account not found.")

        elif choice == '3':
            account_number = input("Enter account number: ")
            amount = float(input("Enter deposit amount: "))
            account = bank.find_account(account_number)
            if account and account.deposit(amount):
                print(f"Deposit successful. New balance: ${account.balance:.2f}")
            else:
                print("Deposit failed. Account not found or invalid amount.")

        elif choice == '4':
            account_number = input("Enter account number: ")
            amount = float(input("Enter withdrawal amount: "))
            account = bank.find_account(account_number)
            if account and account.withdraw(amount):
                print(f"Withdrawal successful. New balance: ${account.balance:.2f}")
            else:
                print("Withdrawal failed. Account not found, insufficient funds, or invalid amount.")

        elif choice == '5':
            from_account = input("Enter your account number: ")
            to_account = input("Enter recipient account number: ")
            amount = float(input("Enter transfer amount: "))
            if bank.transfer_funds(from_account, to_account, amount):
                print("Transfer successful.")
            else:
                print("Transfer failed. Check account numbers and balance.")

        elif choice == '6':
            account_number = input("Enter account number: ")
            account = bank.find_account(account_number)
            if account:
                print("\nAccount Information:")
                print(account.display_info())
            else:
                print("Account not found.")

        elif choice == '7':
            total_interest = bank.add_interest_to_savings()
            print(f"Interest added to all savings accounts. Total interest paid: ${total_interest:.2f}")

        elif choice == '8':
            print("Exiting Bank System.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    bank_menu()