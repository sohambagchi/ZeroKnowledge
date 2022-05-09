import secrets
import random
from sympy.combinatorics.named_groups import CyclicGroup
from sympy import primerange

import time

from Crypto.Util import number

def createGroup(nbits=10):
    return number.getPrime(nbits)

def getGroupGenerators(q, n = 1):
    generatorList = list()
    for g in primerange(q//2, q):
        gen = list()
        G = list(range(q))
        G.remove(0)
        
        p = 1
        stopTime = time.time() + 2
        while len(G) != len(gen) and time.time() < stopTime:
            j = (g**p) % q
            if (j not in gen) and (j in G):
                gen.append(j)
            p += 1
        if len(G) == len(gen):
            generatorList.append(g)
        if len(generatorList) == n:
            if n == 1:
                return generatorList[0]
            else:
                return generatorList

def getExponents(g, x, q):
    return pow(g, x)

def generateParams(q):    
    # all non-identity elements of a cyclic group are generators
    # g = random.randint(0, G.order())
    g = getGroupGenerators(q)
    
    # a random witness
    x = random.randint(0, q)
    
    # y = (g**x) % q
    y = getExponents(g, x, q)
    
    param = {
        "q": q,
        "g": g,
        "y": y
    }
    
    return param, x

if __name__ == '__main__':
    for i in range(100):
        q = createGroup()
        params, witness = generateParams(q)
        
        r = random.randint(1, params['q'])
        a = pow(params['g'], r, params['q'])
        
        c = random.randint(1, params['q'])
        
        t = r + (c * witness)
        
        LHS = pow(params['g'], t, params['q'])    
        RHS = a * pow(params['y'], c, params['q']) % params['q']
        
        print(i, LHS, RHS)
        assert(LHS == RHS)
        