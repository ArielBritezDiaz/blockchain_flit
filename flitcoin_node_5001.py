#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 22:17:51 2024

@author: arieldiaz
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests #para agarrar los nodos correctos cuandos se verifiquen que los nodos están bien
from uuid import uuid4
from urllib.parse import urlparse

#Paso 1: Creación del Blockchain
class Blockchain:
    
    #initial chain
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = "0")
        self.nodes = set()
        
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain) #es la chain que estamos trabajando en el momento
        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            
            #tomamos la cadena más larga
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    
            if longest_chain:
                self.chain = longest_chain
                return True
            
            return False
    
    #create one block
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        
        self.transactions = []
        self.chain.append(block)
        return block
    
    #transactions
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    #get previous block
    def get_previous_block(self):
        return self.chain[-1] #get the last block of chain
    
    def proof_of_work(self, previous_proof):
        new_proof = 1 #we will be to increment the proof by 1 until we get the correct number
        check_proof = False #if the hash is correct, check_proof will be True, because he find the correct answer
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            
            #si el hash comienza con 4 ceros, el proof será true y se habrá encontrado el hash. en caso contrario, se suma un intento de proof of work
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
            
        return new_proof
    
    
    def hash(self, block):
        #codificamos el block para que sea aceptado por el hash operation
        encoded_block = json.dumps(block, sort_keys = True).encode() #le pasamos el bloque que estamos codificando y el diccionario del bloque ordenado por llaves
        return hashlib.sha256(encoded_block).hexdigest()
    
    #paso 8: implementaremos un if si la info del bc es válida, verificamos si: el hash del previous_block es igual a todos los bloques, y que el proof de cada bloque sea válido de acuerdo a nuestro problema definido
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block #actualizaos el previous_block con el hash del block actual
            block_index += 1 #sumamos +1 al index de block, ya que se añadió un bloque a la blockchain
            
        return True
    


#Paso 2: Minando el Blockchain

#creación de web app con flask
app = Flask(__name__)

#creando una dirección para el nodo en port 5001
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()

#minamos un nuveo bloque
@app.route('/mine_block', methods = ['GET'])
def main_block():
    previous_block = blockchain.get_previous_block() #ejecutamos la función declarada en Blockchain en línea 35
    previous_proof = previous_block['proof'] #tomamos el proof del block definido en línea 27
    
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Ariel', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {
        'message': 'Congratulations! You have successfully mined a block of the Flit Blockchain!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }
    
    return jsonify(response), 200

#obteniendo cadena completa
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    
    return jsonify(response), 200

#chequeando validez de cadena de bloques
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {
            'message': 'All correct! The Blockchain is valid!'
        }
    else:
        response = {
            'message': 'Oh no! The Blockchain is not valid!'
        }
    
    return jsonify(response), 200

#agregando nueva transacción al blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json() #contiene la transacción
    transaction_keys = ['sender', 'receiver', 'amount']
    
    if not all (key in json for key in transaction_keys):
        return 'Some element of the transaction is missing', 401
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {
        'message': f'The transaction will be added to the block and the block will be {index}'
    }
    
    return jsonify(response), 201
    

#Paso 3: Descentralizando el Blockchain
#conectando nuevos nodos
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    
    if nodes is None:
        return 'No node', 401
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {
        'message': 'All nodes are now connected. The Flitcoin blockchain contains the following nodes:',
        'total_nodes': list(blockchain.nodes)
    }
    
    return jsonify(response), 201

#reemplazando la cadena por la más larga
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        response = {
            'message': 'The nodes had different chains, so the chain was replaced by the longest one',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'All good, the chain is the longest!',
            'actual_chain': blockchain.chain
        }
    
    return jsonify(response), 200

#corriendo la web app flask
app.run(host = '0.0.0.0', port = '5001')