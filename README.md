# python_blockchain  
I made this very simple blockchain in order to learn about how they work firsthand.

# Usage  
To run the blockchain, use python blockchain.py.  
I tested the program by sending HTTP requests using Postman, the different functions are as follows:  
/mine: Mine a block, which adds the block to the chain.
/chain: Get a JSON response containing the state of the blockchain at this moment  
/nodes/register: Register a node in the network  
/nodes/resolve: Resolve a chain conflict between two nodes: the program will consider the longest node in the network to be the   
authoritative chain.
