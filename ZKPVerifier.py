import socket
import networkx as nx
import json
import pickle
import struct
import random

import graphIsomorphism

from networkx.utils.misc import graphs_equal

HOST = '10.2.34.137'
PORT = 27831

verifier_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
verifier_socket.connect((HOST, PORT))

def sendObject(obj):
    objBytes = pickle.dumps(obj)
    verifier_socket.sendall(struct.pack('>I', len(objBytes)))
    verifier_socket.sendall(objBytes)

def recvObject():
    objSize = struct.unpack('>I', verifier_socket.recv(4))[0]
    payload = b''
    remainingSize = objSize
    while remainingSize > 0:
        payload += verifier_socket.recv(remainingSize)
        remainingSize = objSize - len(payload)
    
    return pickle.loads(payload)
    
def __graphIsomorphism(attack=False):
    commitmentPayload = recvObject()
    
    G_0 = commitmentPayload['G_0']
    G_1 = commitmentPayload['G_1']
    nV = commitmentPayload['nV']
    nE = commitmentPayload['nE']
    
    G_2 = recvObject()
    
    if not attack:
        c = random.choice([0, 1])
        
        sendObject([c])
        
        psi_c = recvObject()
        
        G_c = graphIsomorphism.shuffleVertices(G_0 if c==0 else G_1, psi_c, direction='forward')
        
        print(graphs_equal(G_c, G_2))
        
        assert graphs_equal(G_c, G_2), "Not proved" 
    else:
        sendObject([0, 1])
        
        psi_0 = recvObject()
        psi_1 = recvObject()
        
        phi = graphIsomorphism.splitPermutation(psi_1, psi_0)
        
        G_1_ = graphIsomorphism.shuffleVertices(G_0, phi, direction='forward')
        
        if graphs_equal(G_1_, G_1):
            print("Attack successful, phi obtained")
        else:
            print("Attack failed")
    
    
def __discreteLog(attack=False):
    

def main():
    print("0) Graph Isomorphism")
    print("1) Knowledge of a Discrete Logarithm")
    print("2) Knowledge of an e-th Root Modulo n")
    print("3) Knowledge of Representation")
    print("4) Equality of Discrete Logarithms")
    print("5) Inequality of Discrete Logarithms")
    
    user_choice = input("Enter your choice: ")
    
    verifier_socket.sendall(user_choice.encode())
    
    if int(user_choice) == 0:
        toAttack = int(input("Attack? (0/1): "))
        __graphIsomorphism(False if toAttack==0 else True)
    elif int(user_choice) == 1:
        __discreteLog()
    elif int(user_choice) == 2:
        root()
    elif int(user_choice) == 3:
        knowledgeRepresentation()
    elif int(user_choice) == 4:
        equality()
    elif int(user_choice) == 5:
        inequality()
    else:
        print("Invalid choice")
        exit()
    
    exit()
    
if __name__ == "__main__":
    main()