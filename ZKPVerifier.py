import socket
import networkx as nx
import json
import pickle
import struct
import random
import time
from pprint import pprint

import discreteLog
import graphIsomorphism
import feigeFiatShamir
import root
import equality

from networkx.utils.misc import graphs_equal

HOST = '127.0.0.1'
PORT = 27898

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
    """Prover knows an isomorphism between two graphs, through two permutations. 

    Args:
        attack (bool, optional): _description_. Defaults to False.
    """
    
    print('# ╔═╗┬─┐┌─┐┌─┐┬ ┬  ╦┌─┐┌─┐┌┬┐┌─┐┬─┐┌─┐┬ ┬┬┌─┐┌┬┐ #')
    print('# ║ ╦├┬┘├─┤├─┘├─┤  ║└─┐│ │││││ │├┬┘├─┘├─┤│└─┐│││ #')
    print('# ╚═╝┴└─┴ ┴┴  ┴ ┴  ╩└─┘└─┘┴ ┴└─┘┴└─┴  ┴ ┴┴└─┘┴ ┴ #')
    
    commitmentPayload = recvObject()
    
    G_0 = commitmentPayload['G_0']
    G_1 = commitmentPayload['G_1']
    nV = commitmentPayload['nV']
    nE = commitmentPayload['nE']
    
    print("-------- Received Parameters --------")
    
    pprint({'G_0': G_0.nodes, 'G_1': G_1.nodes, 'Vertices': nV, 'Edges': nE})
    
    G_2 = recvObject()
    
    pprint({'G_2': G_2.nodes})
    
    if not attack:
        c = random.choice([0, 1])
        
        print("Challenge Generated:", c)
        
        sendObject([c])
        
        psi_c = recvObject()
        
        print("Permutation Received: ", end='')
        graphIsomorphism.printIsomorphism(psi_c)
        
        G_c = graphIsomorphism.shuffleVertices(G_0 if c==0 else G_1, psi_c, direction='forward')
        
        pprint({'Permutation Applied': G_c.nodes})
        print("\n\n")
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
    print("-------------------------- END --------------------------\n\n")

def __discreteLog(attack=False):
    
    print('# ╔╦╗┬┌─┐┌─┐┬─┐┌─┐┌┬┐┌─┐  ╦  ┌─┐┌─┐ #')
    print('#  ║║│└─┐│  ├┬┘├┤  │ ├┤   ║  │ ││ ┬ #')
    print('# ═╩╝┴└─┘└─┘┴└─└─┘ ┴ └─┘  ╩═╝└─┘└─┘ #')
    
    print("-------- Received Parameters --------")
    params = recvObject()
    pprint({'q': params['q'], 'g': params['g'], 'y': params['y']})
    
    print("-------- Received Commitment --------")
    commitment = recvObject()
    pprint({'a': commitment})
    
    if not attack:
        c = random.randint(0, params['q'])
    else:
        c = [random.randint(0, params['q']), random.randint(0, params['q'])]
    
    print("Generated Challenge:", c)
    sendObject(c)
    
    t = recvObject()
    
    print("Received Response:", t)

    if not attack:
        LHS = pow(params['g'], t, params['q'])
        RHS = (commitment) * (pow(params['y'], c, params['q'])) % params['q']
        
        pprint({"LHS": LHS, "RHS": RHS})
        
        print(LHS == RHS)
        assert LHS == RHS, "Proof failed"
    else:
        c_ = c[1] - c[0]
        t_ = t[1] - t[0]
        
        c__ = pow(c_, -1, params['q'])
        x = (t_ * c__) % params['q']
        print("Extracted Witness:", x)
        
    print("-------------------------- END --------------------------\n\n")

def __root(attack=False):
    print('# ┌─┐ ┌┬┐┬ ┬  ╦═╗┌─┐┌─┐┌┬┐  ╔╦╗┌─┐┌┬┐┬ ┬┬  ┌─┐ #')
    print('# ├┤───│ ├─┤  ╠╦╝│ ││ │ │   ║║║│ │ │││ ││  │ │ #')
    print('# └─┘  ┴ ┴ ┴  ╩╚═└─┘└─┘ ┴   ╩ ╩└─┘─┴┘└─┘┴─┘└─┘ #')
    
    paramsObj = recvObject()
    
    params = paramsObj['params']
    e = paramsObj['e']
    y = paramsObj['y']
    
    a = recvObject()
    
    if not attack:
        c = random.randint(1, e-1)
    else:
        c = [random.randint(0, e), random.randint(0, e)]
        
    sendObject(c)
    
    t = recvObject()
    
    if not attack:
        LHS = pow(t, e, params['n'])
        RHS = (a * pow(y, c)) % params['n']
        
        print(LHS == RHS)
        
        assert (LHS == RHS), "Proof failed"
    else:
        if t[0] > t[1]:
            t = [t[1], t[0]]
            c = [c[1], c[0]]

        gcd, alpha, beta = root.extendedEuclidGCDAlgorithm(c[1] - c[0], e)
        
        x = (pow(t[1]//t[0], alpha, params['n']) % params['n']) * (pow(y, beta, params['n']) % params['n']) % params['n']
        
        print("Extracted Witness:", x % params['n'])
    
    print("-------------------------- END --------------------------\n\n")

def __knowledgeRepresentation():
    print('# ╦═╗┌─┐┌─┐┬─┐┌─┐┌─┐┌─┐┌┐┌┌┬┐┌─┐┌┬┐┬┌─┐┌┐┌  ┌─┐┌─┐ #')
    print('# ╠╦╝├┤ ├─┘├┬┘├┤ └─┐├┤ │││ │ ├─┤ │ ││ ││││  │ │├┤  #')
    print('# ╩╚═└─┘┴  ┴└─└─┘└─┘└─┘┘└┘ ┴ ┴ ┴ ┴ ┴└─┘┘└┘  └─┘└   #')
    print('#           ╦╔═┌┐┌┌─┐┬ ┬┬  ┌─┐┌┬┐┌─┐┌─┐            #')
    print('#           ╠╩╗││││ │││││  ├┤  │││ ┬├┤             #')
    print('#           ╩ ╩┘└┘└─┘└┴┘┴─┘└─┘─┴┘└─┘└─┘            #')
    
    print("-------- Received Parameters --------")
    
    recvObj = recvObject()
    y = recvObj['y']
    params = recvObj['params']
    
    q = params['q']
    g = params['g']
    h = params['h']
    
    pprint({'Group': {'q': q}, 'Generators': {'g': params['g'], 'h': params['h']}, 'Representation': y })
    
    a = recvObject()
    print("Commitment:", a)
    
    c = random.randint(1, q-1)
    print("Challenge Generated:", c)
    
    sendObject(c)
    
    t = recvObject()
    print("-------- Received Response --------")
    pprint({'t1': t[0], 't2': t[1]})
    
    LHS = (pow(g, t[0], q) * pow(h, t[1], q)) % q
    RHS = a * pow(y, c, q) % q
    
    pprint({"LHS": LHS, "RHS": RHS})
    
    print(LHS == RHS)
    
    assert(LHS == RHS), "Proof failed"
    print("-------------------------- END --------------------------\n\n")



def __equality():
    print('# ╔═╗┌─┐ ┬ ┬┌─┐┬  ┬┌┬┐┬ ┬  ┌─┐┌─┐  ╔╦╗┬┌─┐┌─┐┬─┐┌─┐┌┬┐┌─┐  ╦  ┌─┐┌─┐ #')
    print('# ║╣ │─┼┐│ │├─┤│  │ │ └┬┘  │ │├┤    ║║│└─┐│  ├┬┘├┤  │ ├┤   ║  │ ││ ┬ #')
    print('# ╚═╝└─┘└└─┘┴ ┴┴─┘┴ ┴  ┴   └─┘└    ═╩╝┴└─┘└─┘┴└─└─┘ ┴ └─┘  ╩═╝└─┘└─┘ #')
    
    print('-------- Received Parameters --------')
    params = recvObject()
    
    pprint({'Group': {'q': q}, 'Generators': {'g': params['g'], 'h': params['h']}, 'Elements': {'y': params['y'], 'z': params['z']}})
    
    print('-------- Received Commitment --------')
    commitment = recvObject()
    print("Commitment:", commitment)
    c = random.randint(1, params['q']-1)
    print("Challenge Generated:", c)
    sendObject(c)
    
    t = recvObject()
    print("Response Received:", t)
    LHS1 = equality.getExponents(params['g'], t, params['q'])
    LHS2 = equality.getExponents(params['h'], t, params['q'])
    
    RHS1 = (commitment[0] * pow(params['y'], c, params['q'])) % params['q']
    RHS2 = (commitment[1] * pow(params['z'], c, params['q'])) % params['q']
    
    pprint({"1": {"LHS": LHS1, "RHS": RHS1}, "2": {"LHS": LHS2, "RHS": RHS2}})
    
    print(LHS1 == RHS1 and LHS2 == RHS2)
    
    assert (LHS1 == RHS1 and LHS2 == RHS2), "Proof failed"
    
    print("-------------------------- END --------------------------\n\n")

def __feigeFiatShamir(attack=False):
    print('# ╔═╗┌─┐┬┌─┐┌─┐  ╔═╗┬┌─┐┌┬┐  ╔═╗┬ ┬┌─┐┌┬┐┬┬─┐ #')
    print('# ╠╣ ├┤ ││ ┬├┤───╠╣ │├─┤ │───╚═╗├─┤├─┤││││├┬┘ #')
    print('# ╚  └─┘┴└─┘└─┘  ╚  ┴┴ ┴ ┴   ╚═╝┴ ┴┴ ┴┴ ┴┴┴└─ #')
    recvObj = recvObject()
    print("-------- Received Parameters --------")
    params = {'N': recvObj['N'], 'k': recvObj['k']}
    
    pprint({'N': params['N'], 'k': params['k']})
    
    V = recvObj['V']
    print("------------ Received V -------------")
    
    recvObj = recvObject()
    print("-------- Received Commitment --------")
    r = recvObj['r']
    x = recvObj['x']
    pprint({'r': r, 'x': x})
    
    print("------- Generating Challenge --------")
    A = feigeFiatShamir.getBooleanString(params)
    print(A)
    sendObject(A)
    
    Y = recvObject()
    print("Y:", Y)
    Y2, XV = feigeFiatShamir.computeY2(params, Y, x, V, A)
    
    if all(Y2[_] == XV[_] for _ in range(params['k'])) == True:
        print(True)
    
    assert all(Y2[i] == XV[i] for i in range(params['k'])), "Verification failed"
    
    print("-------------------------- END --------------------------\n\n")


    

def main():
    print("0) Graph Isomorphism")
    print("1) Knowledge of a Discrete Logarithm")
    print("2) Knowledge of an e-th Root Modulo n")
    print("3) Knowledge of Representation")
    print("4) Equality of Discrete Logarithms")
    print("5) Feige-Fiat-Shamir Protocol")
    
    user_choice = input("Enter your choice: ")
    
    verifier_socket.sendall(user_choice.encode())
    
    if int(user_choice) == 0:
        toAttack = int(input("Attack? (0/1): "))
        __graphIsomorphism(False if toAttack==0 else True)
    elif int(user_choice) == 1:
        toAttack = int(input("Attack? (0/1): "))
        __discreteLog(False if toAttack==0 else True)
    elif int(user_choice) == 2:
        toAttack = int(input("Attack? (0/1): "))
        __root(False if toAttack==0 else True)
    elif int(user_choice) == 3:
        __knowledgeRepresentation()
    elif int(user_choice) == 4:
        __equality()
    elif int(user_choice) == 5:
        __feigeFiatShamir()
    else: 
        print("Invalid choice")
        exit()
    
    exit()
    
if __name__ == "__main__":
    main()