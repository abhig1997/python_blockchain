"""
Tryna build a blockchain to learn about why blockchains are so cool.

@author Abhi Gupta
"""


class Blockchain(object):

	def __init__(self):
		self.bchain = []
		self.transactions = []


	def new_block(self):
		# create a new block and add it to this object's bchain
		return


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
		# hash 
		return


	@property
	def last_block(self):
		# return the last (most recent) block in the chain
		pass
	