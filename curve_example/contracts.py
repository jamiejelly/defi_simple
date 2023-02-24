import json
import time
from collections import namedtuple

import requests
import web3
from bs4 import BeautifulSoup
from web3 import Web3, HTTPProvider


# Alchemy free RPC's
NETWORK_2_RPC = {
    "ARBI": "https://arb-mainnet.g.alchemy.com/v2/<KEY>",
    "AVAX": "https://avalanche-mainnet.infura.io/v3/<KEY>",
    "ETH": "https://eth-mainnet.g.alchemy.com/v2/<KEY>",
    # "ETH": "https://rpc.ankr.com/eth", 
    "POLYGON": "https://polygon-mainnet.g.alchemy.com/v2/<KEY>",
}

NETWORK_2_EXPLORER = {
    "ARBI": lambda contract, token_or_address: f"https://arbiscan.io/{token_or_address}/{contract}#code",
    "AVAX": lambda contract, token_or_address: f"https://snowtrace.io/{token_or_address}/{contract}#code",
    "ETH": lambda contract, token_or_address: f"https://etherscan.io/{token_or_address}/{contract}#code",
    "POLYGON": lambda contract, token_or_address: f"https://polygonscan.com/{token_or_address}/{contract}#code",
}

NETWORK_2_EXPORER_API = {
    "ARBI": lambda contract, key: f"https://api.arbiscan.io/api?module=contract&action=getabi&address={contract}&apikey={key}",
    "ETH": lambda contract, key: f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract}&apikey={key}",
    
}

# address, bool: is_token? else False if contract
ADDRESS_POLYGON = {
    "crv": ("0x172370d5cd63279efa6d502dab29171933a610af", True), 
    # commented out ..
    # commented out ..
    # commented out ..
}

ADDRESS_ETH = {

}

# named tuple
ContractSpec = namedtuple('Contract', ['address', 'is_token'])
ADDRESS_POLYGON = {k: ContractSpec(*v) for k, v in ADDRESS_POLYGON.items()}


ADDRESS_BOOK = {
    "POLYGON": ADDRESS_POLYGON,
    "ETH": ADDRESS_ETH,
}


# move to utils?
def convert_balance_2_units(balance, unit="ether"):
    return float(Web3.fromWei(balance, unit=unit))


class ContractFactory:
    
    def __init__(self, network):
        self.network = network.upper()
        self.w3 = Web3(Web3.HTTPProvider(NETWORK_2_RPC[self.network]))

    def create_contract(self, address, is_token: bool):
        address = Web3.toChecksumAddress(address)
        contract = self.w3.eth.contract(
            address=address, 
            abi=self.get_contract_abi(address, 'token' if is_token else 'address'),
        )
        return contract
    
    def get_contract_abi(self, contract, is_token: bool):
        url = NETWORK_2_EXPLORER[self.network](contract, is_token)
        data = requests.get(url, headers = {'User-Agent': 'Popular browser\'s user-agent'})
        html = BeautifulSoup(data.text, 'html.parser')
        abi_html = html.find_all(class_="wordwrap js-copytextarea2")[0]
        abi_json = json.loads(abi_html.next_element)
        return abi_json

    def get_contract_abi_w_api(contract, key):
        # MAX 5 per seconds
        r = requests.get(NETWORK_2_EXPORER_API[self.network](contract, key))
        abi = json.loads(r.json()['result'])
        time.sleep(0.5)
        return abi



# convert to checksum address
def address_2_checksum(dict_):
    dict_ = dict(dict_)
    for network, d in dict_.items():
        for token, add in d.items():
            dict_[network][token] = Web3.toChecksumAddress(add)
    return dict_

# ADDRESSES = {k: Web3.toChecksumAddress(add) for k, add in ADDRESSES.items()}
# CONTRACT = address_2_checksum(CONTRACT)
# TOKENS = address_2_checksum(TOKENS)