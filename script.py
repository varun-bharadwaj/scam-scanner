from flask import Flask, render_template, request

import urllib.request
import json
from bscscan import BscScan

from bscscan.core.sync_client import SyncClient as BscScanSync
import asyncio
API_KEY = 'INSERT_API_KEY'

app = Flask(__name__)

class BSCContract:
    """
    one instance per contract
    """
    
    def __init__(self, code=None, address=None, owner_holdings = 0, *args, **kwargs):
        """Code that the user inputs"""
       
        # assert(code is not None or address is not None)

        # self.code = code
        # self.address = address
        # self.owner_holdings = owner_holdings

        # if code is None and address is not None:
        #     self.code = self.retrieve_src(address)
        
        # self.scam_score = 0
        # self.honey_pot_score = 0
        # self.prior_tokens = 0
        # self.transaction_tracking_score = 0

        self.contractAddress = address

    def honey_pot_check(self):
        
        """
        Code to check for honeypots
        """

    def prior_tokens(self):
        """
        Code to check for prior similar tokens

        # run a code check? 
        # look for coins with the same name?
        # check edit distance between source codes? (highly expensive?) 
        # 

        """
    
    def get_owner_holdings(self):
        pass

    def holdings_check(self):
        """
        check if owner holds more than 5% of liquidity
        """
        if self.total_volume is None:
            self.get_total_volume()
        return self.get_owner_holdings()/self.total_volume > 0.05

    def transaction_tracker(self, owner_address):
        """
        Code to check for owner selling
        """
        if __name__ == "main":
            self.get_first_transaction()

    def get_owner_wallet_address(self):
        '''stuff'''
        with BscScanSync(API_KEY) as client:
            transaction_list = client.get_bep20_token_transfer_events_by_contract_address_paginated(
            contract_address=self.contractAddress,
            page=1,
            offset=100,
            sort="asc"
        )
        return transaction_list[0]['to']

    def get_token_transfers(self, targetAddress):
        print("Contract Address : " + self.contractAddress)
        with BscScanSync(API_KEY) as client:
            transaction_list = client.get_bep20_token_transfer_events_by_address(
                    address= targetAddress,
                    startblock=0,
                    endblock=999999999,
                    sort="asc")
        totalTokensSold = 0
        for transaction in transaction_list:
            if transaction["contractAddress"] == self.contractAddress:
                totalTokensSold += int(transaction["value"])
        return totalTokensSold

    def get_scam_score(self):
        owner_address = self.get_owner_wallet_address()
        print("Owner Address: " + owner_address)
        owner_tokens_sold = self.get_token_transfers(owner_address) // 2
        print("Owner Tokens Sold: " + str(owner_tokens_sold))
        total_volume = self.get_total_volume()
        print("Total volume " + str(total_volume))
        
        percentage_owner_sold = 100 * owner_tokens_sold / total_volume 
        print("Percentage Owner has sold: " + str(percentage_owner_sold))
        return round(percentage_owner_sold, 1)
    
    def get_total_volume(self):
        """
        
        """
        with BscScanSync(API_KEY) as client:
            total_volume = client.get_total_supply_by_contract_address(contract_address="0x07af67b392b7a202fad8e0fbc64c34f33102165b")
        return int(total_volume)

async def get_bnb_balance(wallet_address):
  async with BscScan(API_KEY) as bsc:
    print(await bsc.get_bnb_balance(address=wallet_address))
    
"""
def main():
    while True:
        addy = input(r'Please enter the address of a contract you would like to analyze')
        
        C = BSCContract(code=None, address=addy)
        
        scam_pts = dict()
        
        # do stuff here that will 
        scam_score = sum(scam_pts)

        output_str = ''
        coin_type = ''
        if scam_score < 20:
            output_str = "This is likely a reliable coin"
            coin_type = 'reliable'
        elif scam_score < 40: 
            output_str = "This coin may be less than scrupulous"
            coin_type = 'possibly safe'
        elif scam_score < 60:
            output_str = "We are heading into dangerous territory"
            coin_type = 'sketchy'
        elif scam_score < 80:
            output_str = "Even more danger ahead"
            coin_type = 'dangerous'
        else:
            output_str = "It's hopeless. C'est un 'scam'"
            coin_type = 'basically just a sham'

        print(output_str, '\n')
        print(f"Here's why we found this coin to be a {coin_type}:")
        
        for category in scam_pts.keys():
            print(f'\t{category} points was: {scam_pts[category]}')

        x = input("continue with another address? enter either 'y' or 'n'").lower()

        if x == 'y':
            continue
        elif x == 'n':
            break"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def get_value():
    address = str(request.form['address'])
    print(address)
    contract = BSCContract(address=address)
    scam_score = contract.get_scam_score() + 0.1
    scam_score = min(100, scam_score)
    if scam_score == 0:
        pre_text = "Scam Scanner has detected no indication that this token may be a scam. However, that does not mean that this coin is definately safe, please proceed with caution."
    elif scam_score <= 10:
        pre_text = "Scam Scanner has detected little indication that this token may be a scam as the developer has sold a small portion of their coins. Please proceed with caution."
    elif scam_score <= 50:
        pre_text = "Scam Scanner has detected a large indication that this token my be a scam as the developer has sold a large portion of their tokens. Please proceed with extreme caution"
    else:
        pre_text = "Scam Scanner has detected a very large indication that this token is a scam. This means that it is very likely for you to lose your money if you invest in the coin."
    
    return render_template('pass.html',n = pre_text, a=scam_score)

if __name__ == '__main__':
    app.run(debug=True)
