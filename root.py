from Crypto.Util import number

def modulus(l=20):
    p = number.getPrime(l)
    q = number.getPrime(l)
    n = p * q
    return (n, p, q)

def get_e(k=10):
    return number.getPrime(k)

