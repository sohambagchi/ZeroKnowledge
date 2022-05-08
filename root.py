import random
from pprint import pprint
from Crypto.Util import number

def modulus(l):
    p = number.getPrime(l)
    q = number.getPrime(l)
    n = p * q
    return {"n": n, 'p': p, 'q': q}

def get_e(k):
    return number.getPrime(k)

def getWitness(n, e):
    x = random.randint(1, n-1)
    y = pow(x, e, n)
    return {"x": x, "y": y}

def getCommitment(n, e):
    r = random.randint(1, n-1)
    a = pow(r, e, n)
    return {"a": a, "r": r}

def getChallenge(e):
    c = random.randint(1, e-1)
    return c

def getResponse(r, x, c, n):
    if isinstance(c, int):
        t = r * (pow(x, c, n) % n)
    else:
        t = [r * pow(x, c[0]), r * pow(x, c[1])]
    return t
    
def extendedEuclidGCDAlgorithm(c_, e):
    if c_ == 0:
        return e, 0, 1
    else:
        gcd, alpha, beta = extendedEuclidGCDAlgorithm(e % c_, c_)
        return gcd, beta - (e // c_) * alpha, alpha

if __name__ == '__main__':
    """
        1. Get Params (n, p, q)
        2. Get e (of k bits)
        3. Get y = pow(x, e, n)
        4. Share y
        5. Get commitment a = pow(r, e, n)
        6. Get challenge c = random(1, e-1)
        7. Form response t = r * pow(x, c, n)
    """
    for i in range(100):
        params = modulus(20)
        e = get_e(10)
        witnessObj = getWitness(params['n'], e)
        
        x = witnessObj['x']
        y = witnessObj['y']
        
        commitmentObj = getCommitment(params['n'], e)
        c = getChallenge(e)
        t = getResponse(commitmentObj['r'], x, c, params['n'])

        LHS = pow(t, e, params['n'])
        RHS = (commitmentObj['a'] * pow(y, c)) % params['n']
        
        assert (LHS == RHS), "break"    
    