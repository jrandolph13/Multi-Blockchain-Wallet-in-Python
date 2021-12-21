# Import dependencies
import os
import subprocess 
import json
from dotenv import load_dotenv

from constants import *
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from bit import *
from web3 import Web3
from eth_account import Account 

# Load and set environment variables
load_dotenv()

mnemonic=os.getenv("mnemonic","ridge burst wash eager infant old vocal coast describe wood stove recall")
print(mnemonic)

# Import constants.py and necessary functions from bit and web3
BTC = 'btc'
ETH = 'eth'
BTCTEST = 'btc-test'

w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
w3.eth.getBalance("0x50eE8d6D03f36B893E6483453FBf81FCEbd39857")
from web3.gas_strategies.time_based import medium_gas_price_strategy
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)
 
 
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    print("Inside function")
    command =  f'php ~/hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json'

    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status=p.wait()

    keys =  json.loads(output)

    print(keys)
    return keys 

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = ["eth", "btc-test", "btc"]
numderive = 3 
keys = {}
for coin in coins:
    keys[coin]= derive_wallets(mnemonic, coin, numderive=3)

eth_PrivateKey = keys ["eth"][0]["privkey"]
btc_PrivateKey = keys ["btc-test"][0]["privkey"]

print(json.dumps(eth_PrivateKey, indent=4, sort_keys=True))
print(json.dumps(btc_PrivateKey, indent=4, sort_keys=True))
print(json.dumps(keys, indent=4, sort_keys=True))

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

eth_acc = priv_key_to_account(ETH, eth_PrivateKey)
btc_acc = priv_key_to_account (BTCTEST, btc_PrivateKey)


# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, recipient, amount):
    global trx_data
    if coin ==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        trx_data = {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
        return trx_data

    if coin ==BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)]) 

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipient, amount):
    if coin == "eth":
        tx_eth = create_tx(coin,account, recipient, amount)
        sign = account.signTransaction(tx_eth)
        result = w3.eth.sendRawTransaction(sign.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        trx_btctest= create_tx(coin,account,recipient,amount)
        sign_trx_btctest = account.sign_transaction(trx_btctest)
        from bit.network import NetworkAPI
        NetworkAPI.broadcast_tx_testnet(sign_trx_btctest)       
        return sign_trx_btctest

