from scripts.helper import get_account
from brownie import interface, config, network
from web3 import Web3
from scripts.send import send_message


# Deposited assets and addresses
# This is a bit hard coded - Maybe a programatic solution
assets = { 'mDAI_debt' : "0x75c4d1fb84429023170086f06e682dcbbf537b7d",
           'mUSDC_debt' : "0x248960a9d75edfa3de94f7193eae3161eb349a12",
           'mWMATIC_debt' : "0x59e8e9100cbfcbcbadf86b9279fa61526bbb8765",
           'mWETH_debt' : '0xede17e9d79fc6f9ff9250d9eefbdb88cc18038b5',
           'AAVE_MATIC_WETH' : "0x28424507fefb6f7f8E9D3860F56504E4e5f5f390",
           'AAVE_MATIC_WMATIC' : "0x8dF3aad3a84da6b69A4DA8aeC3eA40d9091B2Ac4",
           'AAVE_MATIC_USDC' : "0x1a13f4ca1d028320a707d99520abfefca3998b7f",
           'AAVE_MATIC_DAI' : "0x27f8d03b3a2196956ed754badc28d73be8830a6e"}

def get_incentive_balance(assets,account):
    incentive = interface.IAaveIncentivesController(config["networks"][network.show_active()]["aave_incetives"])
    balance = incentive.getRewardsBalance(list(assets.values()), account.address)
    return balance

def claim_rewards(assets,account,balance):
    incentive = interface.IAaveIncentivesController(config["networks"][network.show_active()]["aave_incetives"])
    tx = incentive.claimRewards(list(assets.values()), balance, account.address, {"from": account})
    tx.wait(1)
    return tx

def unwrap_all(account):
    wmatic_address = config["networks"][network.show_active()]["wmatic_address"]
    wmatic = interface.IERC20(wmatic_address)
    wmatic_bal = wmatic.balanceOf(account)
    wmatic_interface = interface.WethInterface(config["networks"][network.show_active()]["wmatic_address"])
    tx = wmatic_interface.withdraw(wmatic_bal, {"from": account})
    tx.wait(1)
    return tx

def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

def get_eth_gateway():
    gateway = interface.IWETHGateway(config["networks"][network.show_active()]["eth_gateway"])
    return gateway

def deposit_wmatic(amount,account):
    gateway = get_eth_gateway()
    lending_pool = get_lending_pool()
    tx = gateway.depositETH(lending_pool.address, account.address, 0, {"from": account,"value": amount})
    tx.wait(1)
    print(f"Deposited: {amount/(10**18)} Matic")
    return tx

def main():
    main_act = get_account()
    lev_act = get_account('leverage')

    acoounts = [main_act,lev_act]

    lending_pool = get_lending_pool()

    for account in acoounts:
        bal = get_incentive_balance(assets, account)
        print(f'For account {account.address} balance:')
        print(bal / (10 ** 18))

        if bal > Web3.toWei(1.1, "ether"):
            # Claim - while loop allows for failures which tends to happen
            attempt1 = 0
            claim = False
            while attempt1 <= 10 and claim != True:
                try:
                    # Claim the reward
                    tx1 = claim_rewards(assets, account, bal)
                    tx1.wait(1)
                    claim = True
                except:
                    attempt1 += 1
                    pass
        wmatic_address = config["networks"][network.show_active()]["wmatic_address"]
        wmatic = interface.IERC20(wmatic_address)
        wmatic_bal = wmatic.balanceOf(account)

        if wmatic_bal >= Web3.toWei(1,"ether"):
            # Claim - while loop allows for failures which tends to happen
            attempt2 = 0
            unwrap = False
            while attempt2 <= 10 and unwrap != True:
                print('ABOUT TO ATTEMPT UNWRAP')
                try:
                    tx2 = unwrap_all(account)
                    tx2.wait(1)
                    unwrap = True
                except:
                    attempt2 += 1
                    pass

        # Now redeposit
        # I want different behavior from the two accounts
        matic_balance = account.balance()
        deposit_cond = False
        if account == main_act:
            if matic_balance > Web3.toWei(1, "ether"):
                amount = matic_balance - Web3.toWei(0.2, "ether")
                deposit_cond = True
        if account == lev_act:
            if matic_balance > Web3.toWei(5, "ether"):
                amount = matic_balance - Web3.toWei(5, "ether")
                deposit_cond = True

        if deposit_cond == True:
            deposit = False
            attempt3 = 0
            while attempt3 <= 10 and deposit != True:
                try:
                    tx3 = deposit_wmatic(amount, account)
                    tx3.wait(1)
                    deposit = True
                except:
                    attempt3 += 1
                    pass

                if deposit == True:
                    message = f"""\
                    Subject: Rewards Deposited
                
                    Account:  {account}
    
                    Rewards claimed: {bal/(10**18)} Matic
            
                    Rewards reinvested: {amount/(10**18)}
    
                    Transactions:
                    {tx1}
                    {tx2}
                    {tx3}
                    """
                    send_message()