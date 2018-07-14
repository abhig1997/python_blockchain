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


	def new_transaction(self):
		# add a new transaction to this object's transactions
		return


	@staticmethod
	def hash(block):
		# hash 
		return


	@property
	def last_block(self):
		# return the last (most recent) block in the chain
		pass
	