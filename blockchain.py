import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
"""
Trying to build a blockchain to learn about why blockchains are so cool.

@author Abhi Gupta
"""


class Blockchain(object):

    def __init__(self):
        self.bchain = []
        self.transactions = []

        # create a "genesis" block
        # this block has no predecessors
        self.new_block(proof=100, prev_hash=1)



    def new_block(self, proof, prev_hash):
        """
        Make a new block to add to the blockchain

        :param proof: <int> proof value given by Proof of Value algorithm
        :param prev_hash: <int> hash of the previous block
        :return <dict> new Block
        """

        block = {
            'index':    len(self.bchain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': prev_hash or self.hash(self.bchain[-1])

        }

        # reset this objects list of transactions
        self.transactions = []

        self.bchain.append(block)
        return block



    def new_transaction(self, sender, receiver, amt):
        """
        Create a new transaction to go into the next block

        :param sender: <str> the address of the sender
        :param receiver: <str> the address of the receiver
        :param amt: <int> amount being moved
        :return <int> the index of the block holding this transaction
        """
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amt
            })
        return self.last_block['index'] + 1


    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a given block

        :param block: <dict> Block to create the hash from
        :return <str> the hash of the block
        """
        block_str = json.dumps(block, sort_keys=True).encode() # dictionary needs to be ordered for consistent hashes
        return hashlib.sha256(block_str).hexdigest()


        return


    @property
    def last_block(self):
        # return the last (most recent) block in the chain
        return self.bchain[-1]


    def proof_of_work_algorithm(self, last_proof):
        """
        Proof of Work algorithm, similar to Hashcash idea implemented in Bitcoin

        - Find a number p' such that hash(pp') has 4 leading zeroes, where p is the previous p'
        - p is the previous proof, and p ' is the new proof

        :param last_proof: <int>
        :return <int>
        """
        proof = 0
        while not self.is_valid_proof(last_proof, proof):
        	proof = proof + 1 # increment proof since it is not valid yet

        return proof



    @staticmethod
    def is_valid_proof(last_proof, proof):
    	"""
		Checks whether the proof is valid: Does hash(last_proof, proof) contain 4 leading zeros?

		:param last_proof: <int> Previous Proof
		:param proof: <int> Current proof that is being validated
		:return <bool> True if the proof is valid, False if it not valid
    	"""

    	guess = f'{last_proof}{proof}'.encode() # format the string with the last proof and the checking proof, and encode it
        guess_hash = hashlib.sha256(guess).hexdigest() # Generate the hash
        return guess_hash[:4] == "0000"  # check whether the hash has 4 leading zeroes or not

        
####

# create the Node
app = Flask(__name__)

# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# create the blockchain
blockchain = Blockchain()



# make some routes for the app

# route for mining blocks
@app.route('/mine', methods=['GET'])
def mine():
	return "Placeholder for mining a new block"

# route for adding new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	values = request.get_json()


	# check that the request is valid
	required = ['sender', 'receiver', 'amount']
	if not all(k in values for k in required):
		return "Missing values", 400

	# make a new transaction
	index = blockchain.new_transaction(values['sender'], values['receiver'], values['amount'])

	reponse = {'message': f'Transaction will be added to block {index}'}
	return jsonify(response), 201


# route for getting blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


####
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # run the Flask server on port 5000