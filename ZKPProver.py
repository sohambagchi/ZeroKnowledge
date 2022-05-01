import socket
import threading
import random
import pickle
import struct

import graphIsomorphism

HOST = '10.2.34.137'
PORT = 27831

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
    
def handleClient(connection, address):
    print("New Client:", address)
    
    user_choice = connection.recv(1024).decode()
    
    if int(user_choice) == 0:
        __graphIsomorphism(connection)
    elif int(user_choice) == 1:
        discreteLog()
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