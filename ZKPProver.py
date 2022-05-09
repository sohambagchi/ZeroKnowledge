import socket
import threading
import random
import pickle
import struct
import time

from pprint import pprint

import graphIsomorphism
import discreteLog
import feigeFiatShamir
import knowledgeRepresentation
import root
import equality

HOST = '127.0.0.1'
PORT = 27898

prover_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sendObject(conn, obj):
    objBytes = pickle.dumps(obj)
    conn.sendall(struct.pack('>I', len(objBytes)))
    conn.sendall(objBytes)

def recvObject(conn):
    objSize = struct.unpack('>I', conn.recv(4))[0]
    payload = b''
    remainingSize = objSize
    while remainingSize > 0:
        payload += conn.recv(remainingSize)
        remainingSize = objSize - len(payload)
    
    return pickle.loads(payload)

def __feigeFiatShamir(conn):
    print('# ╔═╗┌─┐┬┌─┐┌─┐  ╔═╗┬┌─┐┌┬┐  ╔═╗┬ ┬┌─┐┌┬┐┬┬─┐ #')
    print('# ╠╣ ├┤ ││ ┬├┤───╠╣ │├─┤ │───╚═╗├─┤├─┤││││├┬┘ #')
    print('# ╚  └─┘┴└─┘└─┘  ╚  ┴┴ ┴ ┴   ╚═╝┴ ┴┴ ┴┴ ┴┴┴└─ #')
    
    print("-------- Generated Parameters --------")
    
    params = feigeFiatShamir.generateLargePrimes(512)
    
    pprint({'p': params['p'], 'q': params['q'], 'N': params['N'], 'k': params['k']})
    
    S = feigeFiatShamir.createSecretNumbers(params)
    print("Witness:", S)
    
    V = feigeFiatShamir.getModularSquare(params, S)
    print("V:", V)
    
    sendObject(conn, {'N': params['N'], 'V': V, 'k': params['k']})
    
    r, x = feigeFiatShamir.commitment(params)
    print("-------- Generated Commitment --------")
    pprint({'r': r, 'x': x})
    sendObject(conn, {'r': r, 'x': x})
    
    A = recvObject(conn)
    print("Challenge:", A)
    
    Y = feigeFiatShamir.computeY(params, r, S, A)
    print("Y:", Y)
    sendObject(conn, Y)
    
    print("-------------------------- END --------------------------\n\n")    

def __discreteLog(conn):
    
    print('╔╦╗┬┌─┐┌─┐┬─┐┌─┐┌┬┐┌─┐  ╦  ┌─┐┌─┐')
    print(' ║║│└─┐│  ├┬┘├┤  │ ├┤   ║  │ ││ ┬')
    print('═╩╝┴└─┘└─┘┴└─└─┘ ┴ └─┘  ╩═╝└─┘└─┘')
    
    q = discreteLog.createGroup(nbits=12)
    params, witness = discreteLog.generateParams(q)    
    
    print("-------- Generated Parameters --------")
    pprint({'q': params['q'], 'g': params['g'], 'y': params['y'], 'Witness': witness})
    
    sendObject(conn, params)
    
    r = random.randint(1, params['q'])
    a = pow(params['g'], r, params['q'])
    
    print("-------- Generated Commitment --------")
    pprint({'r': r, 'a': a})
    
    sendObject(conn, a)

    challenge = recvObject(conn)
    
    print("Received Challenge:", challenge)
    
    if isinstance(challenge, int):
        t = r + (challenge * witness)
    else:
        t = [r + (challenge[0] * witness), r + (challenge[1] * witness)]
        print("Witness:", witness)
    
    print("Generated Response:", t)
    
    sendObject(conn, t)
    
    print("-------------------------- END --------------------------\n\n")

def __graphIsomorphism(conn):
    
    print('# ╔═╗┬─┐┌─┐┌─┐┬ ┬  ╦┌─┐┌─┐┌┬┐┌─┐┬─┐┌─┐┬ ┬┬┌─┐┌┬┐ #')
    print('# ║ ╦├┬┘├─┤├─┘├─┤  ║└─┐│ │││││ │├┬┘├─┘├─┤│└─┐│││ #')
    print('# ╚═╝┴└─┴ ┴┴  ┴ ┴  ╩└─┘└─┘┴ ┴└─┘┴└─┴  ┴ ┴┴└─┘┴ ┴ #')
    
    nV = random.randint(10, 50)
    nE = random.randint(nV, nV*(nV-1)/2)
    G_0 = graphIsomorphism.generateGraph(nV, nE)
    phi = graphIsomorphism.generatePermutation(nV)
    G_1 = graphIsomorphism.shuffleVertices(G_0, phi, direction='forward')
    
    print("-------- Generated Parameters --------")
    
    pprint({'G_0': G_0.nodes, 'G_1': G_1.nodes, 'Vertices': nV, 'Edges': nE})
    
    print("Isomorphism: ", end='')
    graphIsomorphism.printIsomorphism(phi)
    
    sendingObject = {
        'G_0': G_0,
        'G_1': G_1,
        'nV': nV,
        'nE': nE
    }
    
    sendObject(conn, sendingObject)
    
    psi_1 = graphIsomorphism.generatePermutation(nV)
    G_2 = graphIsomorphism.shuffleVertices(G_1, psi_1, direction='forward')

    print('Permutation (psi_1): ', end='')
    graphIsomorphism.printIsomorphism(psi_1)
    
    psi_0 = graphIsomorphism.combinePermutations(psi_1, phi)
    
    print('Permutation (psi_0): ', end='')
    graphIsomorphism.printIsomorphism(psi_0)
    
    sendObject(conn, G_2)
    
    c = recvObject(conn)
    
    print("Challenge Received:", c)
    
    if len(c) == 1:
        if c[0]==0:
            print('Sending Permutation (psi_0): ', end='')
            graphIsomorphism.printIsomorphism(psi_0)
            sendObject(conn, psi_0)
        elif c[0]==1:
            print('Sending Permutation (psi_1): ', end='')
            graphIsomorphism.printIsomorphism(psi_1)
            sendObject(conn, psi_1)
        else:
            print("Incorrect choice")
    else:
        sendObject(conn, psi_0)
        sendObject(conn, psi_1)
    print("-------------------------- END --------------------------\n\n")

def __knowledgeRepresentation(conn):
    
    print('# ╦═╗┌─┐┌─┐┬─┐┌─┐┌─┐┌─┐┌┐┌┌┬┐┌─┐┌┬┐┬┌─┐┌┐┌  ┌─┐┌─┐ #')
    print('# ╠╦╝├┤ ├─┘├┬┘├┤ └─┐├┤ │││ │ ├─┤ │ ││ ││││  │ │├┤  #')
    print('# ╩╚═└─┘┴  ┴└─└─┘└─┘└─┘┘└┘ ┴ ┴ ┴ ┴ ┴└─┘┘└┘  └─┘└   #')
    print('#           ╦╔═┌┐┌┌─┐┬ ┬┬  ┌─┐┌┬┐┌─┐┌─┐            #')
    print('#           ╠╩╗││││ │││││  ├┤  │││ ┬├┤             #')
    print('#           ╩ ╩┘└┘└─┘└┴┘┴─┘└─┘─┴┘└─┘└─┘            #')
    
    nbits = 512
    
    q = knowledgeRepresentation.genParams(nbits)
    generators = knowledgeRepresentation.getGenerators(q, n=2)
    
    print("-------- Generated Parameters --------")
    pprint({'Group': {'q': q}, 'Generators': {'g': generators[0], 'h': generators[1]}})
    
    y = knowledgeRepresentation.getRepresentation(q, generators)
    
    print("---------- Generated Witness ---------")
    pprint({'alpha': y['alpha'], 'beta': y['beta'], 'Representation': y['representation']})
    
    
    sendObj = {"params": {'q': q, 'g': generators[0], 'h': generators[1]}, "y": y['representation']}
    
    sendObject(conn, sendObj)
    
    print("-------- Generated Commitment --------")
    
    commitmentObj = knowledgeRepresentation.getCommitment(q, generators)
    
    pprint({'Exponents': {'r1': commitmentObj['r1'], 'r2': commitmentObj['r2']}, 'Commitment': commitmentObj['commitment']})
    
    sendObject(conn, commitmentObj['commitment'])
    
    c = recvObject(conn)
    print("Challenge Received:", c)
    
    print("---------- Generated Response ---------")
    t = knowledgeRepresentation.getChallengeResponse(c, {'alpha': y['alpha'], 'beta': y['beta']}, {'r1': commitmentObj['r1'], 'r2': commitmentObj['r2']})

    pprint({'t1': t[0], 't2': t[1]})

    sendObject(conn, t)
    print("-------------------------- END --------------------------\n\n")

def __root(conn):
    print('# ┌─┐ ┌┬┐┬ ┬  ╦═╗┌─┐┌─┐┌┬┐  ╔╦╗┌─┐┌┬┐┬ ┬┬  ┌─┐ #')
    print('# ├┤───│ ├─┤  ╠╦╝│ ││ │ │   ║║║│ │ │││ ││  │ │ #')
    print('# └─┘  ┴ ┴ ┴  ╩╚═└─┘└─┘ ┴   ╩ ╩└─┘─┴┘└─┘┴─┘└─┘ #')
    
    print("-------- Generated Parameters --------")
    
    params = root.modulus(20)
    e = root.get_e(10)
    witnessObj = root.getWitness(params['n'], e)
    
    pprint({'Params': params, 'Witness': witnessObj})
    
    x = witnessObj['x']
    y = witnessObj['y']
    
    sendObject(conn, {'params': params, 'e': e, 'y': y})
    
    commitmentObj = root.getCommitment(params['n'], e)
    
    sendObject(conn, commitmentObj['a'])
    
    c = recvObject(conn)
    
    t = root.getResponse(commitmentObj['r'], x, c, params['n'])
    
    if not isinstance(t, int):
        print("Witness:", x % params['n'])
    
    sendObject(conn, t)
    
    print("-------------------------- END --------------------------\n\n")

def __equality(conn):
    print('# ╔═╗┌─┐ ┬ ┬┌─┐┬  ┬┌┬┐┬ ┬  ┌─┐┌─┐  ╔╦╗┬┌─┐┌─┐┬─┐┌─┐┌┬┐┌─┐  ╦  ┌─┐┌─┐ #')
    print('# ║╣ │─┼┐│ │├─┤│  │ │ └┬┘  │ │├┤    ║║│└─┐│  ├┬┘├┤  │ ├┤   ║  │ ││ ┬ #')
    print('# ╚═╝└─┘└└─┘┴ ┴┴─┘┴ ┴  ┴   └─┘└    ═╩╝┴└─┘└─┘┴└─└─┘ ┴ └─┘  ╩═╝└─┘└─┘ #')
    
    print("-------- Generated Parameters --------")
    q = equality.createGroup()
    params, witness = equality.generateParams(q)
    
    pprint({'Group': {'q': q}, 'Generators': {'g': params['g'], 'h': params['h']}, 'Elements': {'y': params['y'], 'z': params['z']}})
    
    sendObject(conn, params)
    
    r = random.randint(1, q - 1)
    
    commitment = (equality.getExponents(params['g'], r, q), equality.getExponents(params['h'], r, q))    
    print("Commitment:", commitment)
    
    sendObject(conn, commitment)
    
    c = recvObject(conn)
    
    print("-------- Received Challenge ----------")
    print(c)
    t = r + (c * witness)
    print("-------- Generated Response ----------")
    print(t)
    sendObject(conn, t)
    
    print("-------------------------- END --------------------------\n\n")

def handleClient(connection, address):
    print("New Client:", address)
    
    user_choice = connection.recv(1024).decode()
    
    if int(user_choice) == 0:
        __graphIsomorphism(connection)
    elif int(user_choice) == 1:
        __discreteLog(connection)
    elif int(user_choice) == 2:
        __root(connection)
    elif int(user_choice) == 3:
        __knowledgeRepresentation(connection)
    elif int(user_choice) == 4:
        __equality(connection)
    elif int(user_choice) == 5:
        __feigeFiatShamir(connection)
    else:
        print("Invalid choice")
        exit()
    

def main():
    prover_socket.bind((HOST, PORT))
    prover_socket.listen(10)

    try:
        while True:
            connection, address = prover_socket.accept()
            threading.Thread(target=handleClient, args=(connection, address, )).start()

    except KeyboardInterrupt:
        pass
    
    prover_socket.close()

if __name__ == '__main__':
    main()