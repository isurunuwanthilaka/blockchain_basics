import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask,jsonify,request
from textwrap import dedent


class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.currentTransactions = []
		self.newBlock(previousHash = 1, proof = 100) # Creating a genisis : initiating block without predecessors.


	def newBlock(self,proof,previousHash = None):
		"""
		Create a new block in the blockchain

		:param previousHash: <str> Hash of the previous block
		:param proof: <int> Proof Of Work
		:return:<dict> New Block

		"""

		block = {
		'index':len(self.chain)+1,
		'timestamp':time(),
		'transaction':self.currentTransactions,
		'proof':proof,
		'previousHash':previousHash or self.hash(self.chain[-1])
		}

		self.chain.append(block)
		self.currentTransactions = []
		return block
		
	def newTransaction(self, sender, recipient, amount):
		"""
		Creates a new transaction to go into the next mined Block

		:param sender: <str> Address of the sender
		:param recipient: <str> Address of the recipient
		:param amount: <int> Amount of the transaction
		:return: <int> Index of the block that will hold this transaction

		"""
		self.currentTransactions.append({'sender':sender,'recipient':recipient,'amount':amount})

		return  self.lastBlock['index'] + 1

	@staticmethod
	def hash(block):
		"""
		Create a SHA-256 hash of the block

		:param block:<json> block
		:return:<str>

		"""

		blockString = json.dumps(block, sort_keys = True).encode()
		return hashlib.sha256(blockString).hexdigest()

	@property
	def lastBlock(self):
		return self.chain[-1]


	def proofOfWork(self,lastProof):
		"""
		Simple proof of work algorithm
		-find a number p' s.t. hash(pp') containing leading 4 zeros where the previous p'
		-p is the previous proof and p' is the new proof
		
		:param lastProof:<int>
		:return :<int> New proof

		"""
		proof = 0

		while self.validProof(proof,lastProof) is False:
			proof+=1

		return proof

	@staticmethod
	def validProof(proof,lastProof):
		"""
		Validate POW : hash(proof*lastProof) contains leading 4 zeros?

		:param proof:<int> New Proof
		:param lastProof:<int> Previous Proof
		:return:<boolean>

		"""
		guess = str(proof*lastproof).encode()
		guessHash = hashlib.sha256(guess).hexdigest()
		return guessHash[:4]=='0000'



#Instantiate our Node

app = Flask(__name__)

#Generate a globally unique address for this node

nodeIdentifier = str(uuid4()).replace('-','')

#instantiate the blockchain

blockchain = Blockchain()

@app.route('/mine',methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']}
    return jsonify(response), 200

@app.route('/transactions/new',methods=['POST'])
def newTransaction():
        values = request.get_json()
        #check that the required fields are in the POST'ed data
        required = ['sender','recipient','amount']
        if not all(k in values for k in required):
                return 'Missing values',400

        #Create a new Transaction
        index = blockchain.newTransaction(values['sender'],values['recipient'],values['amount'])
        response ={'message':"Transaction will be added to Block"+str(index)}
        return jsonify(response),201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


        
@app.route('/chain',methods=['GET'])
def fullChain():
        response = {
                'chain':blockchain.chain,
                'length':len(blockchain.chain),
                }
        return jsonify(response),200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

app.run(host='127.0.0.1', port=port)

















	
