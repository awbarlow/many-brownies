from scripts.send import send_message
from scripts.helper import get_account

def main():
    account1 = get_account()
    account2 = get_account('leverage')

    message = f"""\ 
            Subject: Balances Checked  
            
            In account {account1.address}  
            
            You had a MATIC Balance of: {account1.balance()}  
            
            In account {account2.address}  
            
            You had a MATIC Balance of: {account2.balance()}  
            """
    
    send_message(message)