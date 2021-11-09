from scripts.helper import get_account

def main():
    account = get_account()
    print(account)

    act2 = get_account('leverage')
    print(act2.balance())