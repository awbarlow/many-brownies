from brownie import accounts, network, config
import scripts.citrus as citrus

# Networks that we work with
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev", "polygon-fork"]

def get_account(squeeze_type=None):
    # If we are working with a local chain
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV or network.show_active() in FORKED_LOCAL_ENV:
        return accounts[0]
    else:
        return accounts.add(orange_juice(squeeze_type))

def orange_juice(squeeze_type):
    if squeeze_type == None:
        str_ = citrus.main
        juice = config["wallets"]["from_key"]
        juice = juice + str_
    elif squeeze_type == 'leverage':
        str_ = citrus.lev
        juice = config["wallets"]["lev_key"]
        juice = juice + str_
    return juice