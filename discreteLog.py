import secrets
from sympy.combinatorics.named_groups import CyclicGroup

from Crypto.Util import number

def createGroup(q=number.getPrime(20)):
    G = CyclicGroup(q)
    
    param = (G, q, G.generators)
    
    # print(param)
    
    print(G.generators)
    
createGroup()