import random
from pprint import pprint
from Crypto.Util import number


def generateLargePrimes(nbits):
    """Returns p, q, N and k

    Args:
        nbits (int): number of bits

    Returns:
        dict: a dictionary containing p, q, N and k
    """
    p = number.getPrime(nbits)
    q = number.getPrime(nbits)
    N = p * q
    # k = random.randint(1, number.getRandomInteger(int(nbits*0.05)))
    # k = 20
    k = random.randint(1, 100)
    return {'p': p, 'q': q, 'N': N, 'k': k, 'nbits': nbits}

def createSecretNumbers(params):
    S = list()
    for i in range(params['k']):
        S.append(number.getStrongPrime(params['nbits'], e=params['N']))
    return S

def getModularSquare(params, S):
    V = list()
    for s in S:
        V.append(s**2 % params['N'])
    return V

def commitment(params):
    r = random.randint(1, params['N'])
    s = random.choice([-1, 1])
    x = (s * (r**2)) % params['N']
    return r, x

def getBooleanString(params):
    A = list()
    for i in range(params['k']):
        A.append(random.choice([0, 1]))
    return A

def computeY(params, r, S, A):
    Y = list()
    for i in range(params['k']):
        Y.append((r * (S[i]**A[i])) % params['N'])
    return Y

def computeY2(params, Y, x, V, A):
    Y2 = list()
    for y in Y:
        Y2.append((y**2) % params['N'])
    
    XV = list()
    
    for i in range(params['k']):
        XV.append((x * (V[i]**A[i])) % params['N'])
    
    return Y2, XV
    
if __name__ == '__main__':
    nbits = 512
    
    # 1. Get p, q
    # 2. Get N
    # 3. Get k
    params = generateLargePrimes(512)
    pprint(params)

    print("----------------------S----------------------------")
    
    # 4. Get S_0 to S_k
    S = createSecretNumbers(params)
    pprint(S[1:10])
    
    print("----------------------V----------------------------")
    # 5. Get V from S
    V = getModularSquare(params, S)
    pprint(V[1:10])
    # 6. Send V to V
    
    # 7. Choose s and r
    # 8. Calculate x = s r^2
    r, x = commitment(params)
    
    # 9. Victor sends A = a_0 to a_k
    A = getBooleanString(params)
    
    # 10. Peggy computes Y = r s_i ^ a_i
    Y = computeY(params, r, S, A)
    
    # 11. Victor computes Y^2
    # 12. Victor computes x v_0 ^ a^0
    Y2, XV = computeY2(params, Y, x, V, A)

    print("----------------")
    print(Y2)
    print("----------------")
    print(XV)

    for i in range(len(Y2)):
        if (Y2[i] != XV[i]):
            print(Y2[i], XV[i])
        else:
            print(Y2[i] == XV[i])