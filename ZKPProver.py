import socket
import threading
import random
import pickle
import struct
import time

import graphIsomorphism
import discreteLog
import feigeFiatShamir
import knowledgeRepresentation
import root
import equality

HOST = '10.2.57.30'
PORT = 27892

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
    params = feigeFiatShamir.generateLargePrimes(512)
    
    S = feigeFiatShamir.createSecretNumbers(params)
    V = feigeFiatShamir.getModularSquare(params, S)
    
    sendObject(conn, {'N': params['N'], 'V': V, 'k': params['k']})
    
    r, x = feigeFiatShamir.commitment(params)
    
    sendObject(conn, {'r': r, 'x': x})
    A = recvObject(conn)
    
    Y = feigeFiatShamir.computeY(params, r, S, A)
    sendObject(conn, Y)
    

def __discreteLog(conn):
    # q = discreteLog.generateLargePrime(10)
    q = discreteLog.createGroup()
    params, witness = discreteLog.generateParams(q)
    
    sendObject(conn, params)
    
    r = random.randint(1, params['q'])
    a = pow(params['g'], r, params['q'])
    
    sendObject(conn, a)

    challenge = recvObject(conn)
    
    if isinstance(challenge, int):
        t = r + (challenge * witness)
    else:
        t = [r + (challenge[0] * witness), r + (challenge[1] * witness)]
        print("Witness:", witness)
    
    
    sendObject(conn, t)

def __graphIsomorphism(conn):
    nV = random.randint(10, 50)
    nE = random.randint(nV, nV*(nV-1)/2)
    G_0 = graphIsomorphism.generateGraph(nV, nE)
    phi = graphIsomorphism.generatePermutation(nV)
    G_1 = graphIsomorphism.shuffleVertices(G_0, phi, direction='forward')
    
    sendingObject = {
        'G_0': G_0,
        'G_1': G_1,
        'nV': nV,
        'nE': nE
    }
    
    sendObject(conn, sendingObject)
    
    psi_1 = graphIsomorphism.generatePermutation(nV)
    G_2 = graphIsomorphism.shuffleVertices(G_1, psi_1, direction='forward')

    psi_0 = graphIsomorphism.combinePermutations(psi_1, phi)
    
    sendObject(conn, G_2)
    
    c = recvObject(conn)
    
    if len(c) == 1:
        if c[0]==0:
            sendObject(conn, psi_0)
        elif c[0]==1:
            sendObject(conn, psi_1)
        else:
            print("Incorrect choice")
    else:
        sendObject(conn, psi_0)
        sendObject(conn, psi_1)

def __knowledgeRepresentation(conn):
    nbits = 512
    
    q = knowledgeRepresentation.genParams(nbits)
    generators = knowledgeRepresentation.getGenerators(q, n=2)
    
    y = knowledgeRepresentation.getRepresentation(q, generators)
    
    sendObj = {"params": {'q': q, 'g': generators[0], 'h': generators[1]}, "y": y['representation']}
    
    sendObject(conn, sendObj)
    
    commitmentObj = knowledgeRepresentation.getCommitment(q, generators)
    
    sendObject(conn, commitmentObj['commitment'])
    
    c = recvObject(conn)
    
    t = knowledgeRepresentation.getChallengeResponse(c, {'alpha': y['alpha'], 'beta': y['beta']}, {'r1': commitmentObj['r1'], 'r2': commitmentObj['r2']})
    
    sendObject(conn, t)

def __root(conn):
    params = root.modulus(20)
    e = root.get_e(10)
    witnessObj = root.getWitness(params['n'], e)
    
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

def __equality(conn):
    q = equality.createGroup()
    params, witness = equality.generateParams(q)
    
    sendObject(conn, params)
    
    r = random.randint(1, q - 1)
    
    commitment = (equality.getExponents(params['g'], r, q), equality.getExponents(params['h'], r, q))
    
    sendObject(conn, commitment)
    
    c = recvObject(conn)
    
    t = r + (c * witness)
    
    sendObject(conn, t)

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