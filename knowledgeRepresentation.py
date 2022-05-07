import discreteLog
import random

def genParams(nbits):
    return discreteLog.createGroup()
    
def getGenerators(q, n):
    return discreteLog.getGroupGenerators(q, n=n)
    
def getRepresentation(q, generators):
    alpha = random.randint(1, q-1)
    beta = random.randint(1, q-1)
    
    representation = (discreteLog.getExponents(generators[0], alpha, q) * discreteLog.getExponents(generators[1], beta, q)) % q
    
    return {'alpha': alpha, 'beta': beta, 'representation': representation}
    
def getCommitment(q, generators):
    r1 = random.randint(1, q-1)
    r2 = random.randint(1, q-1)
    
    commitment = (discreteLog.getExponents(generators[0], r1, q) * discreteLog.getExponents(generators[1], r2, q)) % q
    
    return {'r1': r1, 'r2': r2, 'commitment': commitment}
    
    
def getChallengeResponse(challenge, witness, randoms):
    return (randoms['r1'] + (challenge * witness['alpha']), randoms['r2'] + (challenge * witness['beta']))

if __name__ == '__main__':
    genParams(nbits=10)