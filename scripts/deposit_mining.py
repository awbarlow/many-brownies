from brownie import interface, config, network, accounts
from scripts.helper import get_account
from scripts.send import send_deposit_update,send_message

LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev", "polygon-fork"]

def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

def main():
    account = get_account()

    print(account)
    print(network.show_active())

    # Get lending pool interface
    lending_pool = get_lending_pool()


    weth_address = config["networks"][network.show_active()]["weth_address"]
    weth = interface.IERC20(weth_address)

    weth_bal = weth.balanceOf(account)

    print(weth_bal)

    if weth_bal > 0:
        tx1 = lending_pool.deposit(weth_address, weth_bal, account.address, 0, {"from": account})
        tx1.wait(1)
        send_deposit_update(weth_bal,tx1,health)

    # See account stats
    list_ = lending_pool.getUserAccountData(account)
    health = list_[5]/(10**18)

    if health < 1.2:
        message = f"""\
        Subject: AAVE HEALTH ALERT

        You had a health  of: {health}
        """
        send_message(message)