import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
import random
import time

from pprint import pprint

def combinePermutations(P2, P1):
    """
        Combines two permutations into one permutation.
    """
    P3_forward = dict()
    P3_backward = dict()
    
    for k, v in P1[0].items():
        P3_forward[k] = P2[0][v]

    for k, v in P1[1].items():
        P3_backward[k] = P2[1][v]
    
    return (P3_forward, P3_backward)

def splitPermutation(P2, P3):
    P1_forward = dict()
    P1_backward = dict()
    
    for k, v in P3[0].items():
        P1_forward[k] = P2[1][v]
        P1_backward[v] = P2[0][k]
    
    return (P1_forward, P1_backward)
    

def generatePermutation(n):
    forwardPermutation = dict()
    backwardPermutation = dict()
    
    rng = np.random.default_rng()
    
    oldLabels = list(range(n))
    newLabels = list(rng.permutation(oldLabels))
    
    for _, i in enumerate(newLabels):
        forwardPermutation[_] = oldLabels.index(i)
        backwardPermutation[oldLabels.index(i)] = _
    
    return (forwardPermutation, backwardPermutation)
        

def shuffleVertices(G, permutations=None, direction='forward'):
    """
        Shuffle the vertices of a graph.
    
        Parameters
        ----------
        
        G: networkx.Graph
            The graph to shuffle.
            
        permutation: tuple of dict (Default: None)
            A tuple containing a forward and a backward permutation. Use 
            generatePermutation(n) to generate a permutation of this type.

        direction: str (Default: 'forward')
            The direction of the permutation. This will determine which of 
            the two permutations to pick from the permutation tuple.
    
    """
    if permutations is None:
        permutations = generatePermutation(len(G.nodes()))
    
    permutation = permutations[0] if direction=='forward' else permutations[1]
    
    currentLabels = list(G.nodes())
    
    newLabels = [ 0 for i in range(len(G.nodes())) ]
    
    for k, v in permutation.items():
        newLabels[k] = currentLabels[v]
    
    return nx.relabel_nodes(G, permutation, copy=True)

def generateGraph(n, m):
    G = nx.gnm_random_graph(n, m)
    # nx.draw(G)
    # plt.show()
    return G

def main():
    A = generateGraph(10, 17)
    print(A.nodes())
    time.sleep(3)
    
    
if __name__ == '__main__':
    # graphOne = generateGraph(15, 30)

    
    # p_0 = generatePermutation(len(graphOne.nodes()))
    # graphTwo = shuffleVertices(graphOne, p_0, direction='forward')
    
    # p_1 = generatePermutation(len(graphTwo.nodes()))
    # graphThree = shuffleVertices(graphTwo, p_1, direction='forward')
    
    
    # graphTwo_ = shuffleVertices(graphThree, p_1, direction='backward')
    
    
    # graphOne_ = shuffleVertices(graphTwo_, p_0, direction='backward')
    
    # p_2 = combinePermutations(p_0, p_1)
    
    # graphThree_ = shuffleVertices(graphOne_, p_2, direction='forward')
    
    
    # nV  = random.randint(10, 50)
    nV = 10
    nE  = random.randint(nV, nV*(nV-1)/2)
    
    G_0 = generateGraph(nV, nE)
    
    phi = generatePermutation(nV)
    G_1 = shuffleVertices(G_0, phi, direction='forward')
    
    psi_1 = generatePermutation(nV)
    G_2   = shuffleVertices(G_1, psi_1, direction='forward')
    
    psi_0 = combinePermutations(psi_1, phi)
    
    G_3 = shuffleVertices(G_0, psi_0, direction='forward')
    
    print(G_0.nodes())
    print(G_1.nodes())
    print(G_2.nodes())
    print(G_3.nodes())
    
    print("")
    
    print(phi)
    print(psi_1)
    print(psi_0)
    
    print(splitPermutation(psi_1, psi_0))
    
    # print()
    
    # p = generatePermutation(15)
    
    # pprint(p)
    # main()