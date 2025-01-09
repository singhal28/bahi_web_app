# Sample Users and Ledger Accounts data

users = [
    {'id': 1, 'email': 'ris@gmail.com', 'password': '123'},
    {'id': 2, 'email': 'jane.smith@example.com', 'password': 'password456'},
]

ledger_accounts = [
    {'id': 1, 'user_id': 1, 'name': 'Checking Account', 'balance': 5000, 'transactions': []},
    {'id': 2, 'user_id': 1, 'name': 'Savings Account', 'balance': 10000, 'transactions': []},
    {'id': 3, 'user_id': 2, 'name': 'Credit Account', 'balance': -200, 'transactions': []},
]

def get_users():
    return users

def get_user_by_email(email):
    return next((user for user in users if user['email'] == email), None)

def get_ledger_accounts():
    return ledger_accounts

def add_transaction(account_id, transaction_type, amount, description):
    account = next((acct for acct in ledger_accounts if acct['id'] == account_id), None)
    if account:
        transaction = {
            'type': transaction_type,
            'amount': amount,
            'description': description,
            'balance': account['balance'] + amount if transaction_type == 'credit' else account['balance'] - amount
        }
        account['transactions'].append(transaction)
        account['balance'] = transaction['balance']
