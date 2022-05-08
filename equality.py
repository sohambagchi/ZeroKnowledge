import secrets
import random
import time
from pprint import pprint

from Crypto.Util import number

import discreteLog

def createGroup(nbits=7):
    return number.getPrime(nbits)

def getGroupGenerators(q, n=2):
    return discreteLog.getGroupGenerators(q, n)

def getExponents(g, x, q):
    return pow(g, x, q)

def generateParams(q):
    x = random.randint(0, q)
    
    g = None
    while g == None:
        g = getGroupGenerators(q)
        
    y = getExponents(g[0], x, q)
    z = getExponents(g[1], x, q)
    
    param = {
        'q': q,
        'g': g[0],
        'h': g[1],
        'y': y,
        'z': z
    }
    
    return param, x
    
if __name__ == '__main__':
    q = createGroup()
    params, witness = generateParams(q)
    
    pprint(params)
    
    print(2, witness)
    
    r = random.randint(1, q)
    
    print(3, r)
    
    commitment = (getExponents(params['g'], r, q), getExponents(params['h'], r, q))
    
    print(commitment)
    
    challenge = random.randint(1, q)
    
    print(challenge)
    
    t = r + ((challenge * witness) )
    
    print(t)
    
    LHS1 = getExponents(params['g'], t, q)
    LHS2 = getExponents(params['h'], t, q)
    
    RHS1 = (commitment[0] * pow(params['y'], challenge, q)) % q
    RHS2 = (commitment[1] * pow(params['z'], challenge, q)) % q
    
    print(LHS1, RHS1)
    print(LHS2, RHS2)