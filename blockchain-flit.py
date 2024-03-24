#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 17:40:32 2024

@author: arieldiaz
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify

#Paso 1: Creación del Blockchain
class Blockchain:
    
    #initial chain
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = "0")
    
    #create one block
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
        
        self.chain.append(block)
        return block
    
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
blockchain = Blockchain()

#minamos un nuveo bloque
@app.route('/mine_block', methods = ['GET'])
def main_block():
    previous_block = blockchain.get_previous_block() #ejecutamos la función declarada en Blockchain en línea 35
    previous_proof = previous_block['proof'] #tomamos el proof del block definido en línea 27
    
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {
        'message': 'Congratulations! You have successfully mined a block of the Flit Blockchain!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
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

#corriendo la web app flask
app.run(host = '0.0.0.0', port = '5000')