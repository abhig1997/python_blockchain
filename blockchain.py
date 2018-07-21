import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from urllib.parse import urlparse


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


        # track the other nodes in the network
        self.nodes = set()


    def is_valid_chain(self, chain):
        """
        Check if a given chain is valid

        :param chain: <list> blockchain to check for validity
        :return: <bool> True if the chain is valid, False if it is not valid
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            a_str = str(last_block)
            print(a_str)
            a_str = str(block)
            print(a_str)
            print("\n-----------\n")
            # check that the hash of the block is correct

            if block['previous_hash'] != self.hash(last_block):
            	return False

            # check that the proof of work is correct
            if not self.is_valid_proof(last_block['proof'], block['proof']):
            	return False


            last_block = block
            current_index = current_index + 1

        return True



    def resolve_conflicts(self):
    	"""
		Consensus algorithm, resolves conflicts with other
		nodes by replacing current chain with the longest one
		in the network

		:return: <bool> True if our chain was replaced, False if it 
		wasn't replaced
    	"""

    	neighbors = self.nodes
    	new_chain = None

    	# looking for chains longer than ours
    	max_length = len(self.bchain)

    	# grab and verify the chains from all nodes in our network
    	for node in neighbors:
    		response = requests.get(f'http://{node}/chain')

    		if response.status_code == 200:
    			length = response.json()['length']
    			chain = response.json()['chain']

    			# check if the length is longer and the chain is valid
    			if length > max_length and self.is_valid_chain(chain):
    				max_length = length
    				new_chain = chain


    	if new_chain:
    		self.chain = new_chain
    		return True

    	return False



    def register_node(self, address):
        """
        Add a new node to this object's list of nodes

        :param address: <str> The address of the node
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) # add the address of the new node to the list of nodes



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
        return guess_hash[:4] == "1234"  # check whether the hash has 4 leading zeroes or not

        
####

# create the Node
app = Flask(__name__)

# generate a globally unique address for this node
node_addr = str(uuid4()).replace('-', '')

# create the blockchain
blockchain = Blockchain()



# make some routes for the app

# route for mining blocks
@app.route('/mine', methods=['GET'])
def mine():
    # use Proof of work algo to get next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work_algorithm(last_proof)

    # need to ensure that there is a reward for finding the proof
    # the sender is '0' to show that there is a new coin mined
    blockchain.new_transaction(
        sender="0",
        receiver=node_addr,
        amt=1
    )


    # make a new black and add it to the chain
    prev_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, prev_hash)

    response = {
        'message': 'New block created',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    # return the json version of the response dictionary
    return jsonify(response), 200




# route for adding new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()


    # check that the request is valid
    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # make a new transaction
    index = blockchain.new_transaction(values['sender'], values['receiver'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201


# route for getting blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.bchain,
        'length': len(blockchain.bchain),
    }
    return jsonify(response), 200


# route to register nodes
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
	values = request.get_json()

	nodes = values.get('nodes')

	if nodes is None:
		return "Error: List is not a valid list of nodes", 400

	for node in nodes:
		# register all the nodes
		blockchain.register_nodes(node)


	response = {
		'message': 'New nodes have been registered',
		'total_nodes': list(blockchain.nodes)
	}
	return jsonify(response), 201


# route to resolve conflicts between nodes
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'This chain was replaced due to node conflicts',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is the longest chain, and therefore the authority for this blockchain',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


####
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # run the Flask server on port 5000