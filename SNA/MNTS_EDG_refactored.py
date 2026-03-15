'''
@author: Marcus Kesper, marcus.kesper@bluewin.ch, 
FFHS Fernfachhochschule Schweiz

Version 1.0 31.01.2013

Python-Programm zur Bachelor-Thesis im Studiengang Informatik
Social Network Analysis
Cliquenanalyse unter Beruecksichtigung von Intensitaet und Gegenseitigkeit der 
Kommunikation
'''

import csv #standard module
import logging #standard module
import numpy as np
import random #standard module
import time #standard module
import sys #standard module
import optparse #standard module
import pandas as pd

# Funktion: Liest einen DIMACS-Graphen ein. Die Funktion wurde von
# http://www.dcc.fc.up.pt/~jpp/code/partition/graphtools.py uebernommen
# und fuer diese Anwendung angepasst.
# Rueckgabewert: Ein zweidimensionales Array
def read_DIMACS_graph(filename):
    '''
    Read a graph from a file in the format specified by David Johnson
    for the DIMACS clique challenge.
    Instances are available at
    ftp://dimacs.rutgers.edu/pub/challenge/graph/benchmarks/clique
    '''
    myArr = np.int_([[]])
    try:
        if len(filename) > 3 and filename[-3:] == ".gz":  # file compressed with gzip
            import gzip
            f = gzip.open(filename, "rt")
        else:   # usual, uncompressed file
            f = open(filename, "rt")
    except IOError:
        print("could not open file", filename)
        exit(-1)

    for line in f:
        if line[0] == 'e':
            e, i, j = line.split()
            i, j = int(i) - 1, int(j) - 1 # -1 for having nodes index starting on 0
            myArr[i][j] = 1
        elif line[0] == 'c':
            continue
        elif line[0] == 'p':
            p, name, n, nedges = line.split()
            # assert name == 'clq'
            n, nedges = int(n), int(nedges)
            myArr = np.int_([[0] * n for i in range(n)])
        else:
            print("the file", filename,"is not in DIMACS format")
            exit(-1)
    f.close()
    return myArr

def readFile_fast(filename):
    try:
        df = pd.read_csv(filename, delimiter=';', header=None, dtype=int)
        return df.values
    except FileNotFoundError:
        print("could not open file", filename)
        exit(-1)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        exit(-1)

# Funktion: Fuellt ein Array mit Nullen
# Rueckgabewert: Das mit Nullen gefuellte Array
def initialize(size):
    return np.zeros((size, size), dtype=np.int_)

# Funktion: Fuellt ein Array einer bestimmten Dichte mit Zufallswerten
# Rueckgabewert: Das gefuellte Array
def fillRandomAdv(myArr, density):
    nrOfActors = myArr.shape[0]
    nrofEdgesPerVertex = float((nrOfActors - 1) * density)
    randVal1 = random.randint(80, 100)
    iMax = int(nrOfActors // 100 * randVal1)
    i = 0
    for acteur in randrange(0, nrOfActors - 1):
        i = i + 1
        if i > iMax:
            break  
        nrofEdgesPerVertexRandom = random.randint(int(nrofEdgesPerVertex - nrofEdgesPerVertex // 5), int(nrofEdgesPerVertex + nrofEdgesPerVertex // 5))
        for contacts in range(int(nrofEdgesPerVertexRandom // 2)):
            randVal2 = random.randint(0, 100)
            randVal3 = random.randint(0, 100)
            randAkt = random.randint(0, nrOfActors - 1)
            myArr[acteur][randAkt] = randVal2
            myArr[randAkt][acteur] = randVal3
    return myArr

# Funktion: Gibt ein Array auf die Konsole aus
# nur fuer Tests, wird sonst nicht benutzt
def showArray(myArr):
    nrOfActors = myArr.shape[0]
    for i in range(nrOfActors):
        print(i, ': ', end=' ')
        for j in range(nrOfActors):
            print(myArr[i][j], end=' ')
        print('')

# Funktion: Testet, ob die Netzwerkgroesse in einem Bereich liegt, der
# verarbeitet werden kann
# Rueckgabewert: True oder False
def sizeOk(myArr):
    return ((myArr.shape[0] >= 10) and (myArr.shape[0] <= 22000))

# Funktion: Liest ein Array von einem CSV-File
# Rueckgabewert: Das eingelesene Array mit dem Filenamen filename
def readFile(filename):
    try:
        newArr = np.genfromtxt(filename, delimiter=';', dtype=int)
    except IOError:
        print("could not open file", filename)
        exit(-1) 
    return newArr

# Funktion: Schreibt ein Array in ein CSV-File
def writeFile(myArr, filename):
    f = open(filename, "w", newline='')
    myWriter = csv.writer(f, delimiter=';')
    myWriter.writerows(myArr)
    f.close()

# Funktion: Spiegelt ein Array. Wird gebraucht, um Cliquen in ungerichteten Graphen 
# (z.B. in DIMACS Graphen) zu finden
# Rueckgabewert: Das gespiegelte Array 
def mirror(myArr):
    nrOfActors = myArr.shape[0]
    for i in range(nrOfActors):
        for j in range(i):
            myArr[j][i] = myArr[i][j]
    return myArr

# Funktion: Kreiert einen gerichteten und kantengewichteten Graphen mit Cliquen 
# unterschiedlicher Laenge
# Rueckgabewert: Ein Graph als zweidimensionales Array der Groesse size
def createSampleEDG(size):
    nrOfCliques = int(size * 0.001 + 5)
    edg = initialize(size)
    if (size <= 100):
        density = 0.05
    if size > 100 and size <= 10000:
        density = 0.01
    if size > 10000 and size <= 20000:
        density = 0.005
    if size > 20000:
        density = 0.001
    randEDG = fillRandomAdv(edg, density)
    clqs = []
    for randCLQ in range(nrOfCliques):
        clq = []
        if size <= 100:
            clqlength = 4
        else:
            clqlength = random.randint(4, size // 400 + 10) 
        while len(clq) < clqlength:
            member = random.randint(0, size - 1)
            if member not in clq:
                clq.append(member)
        for acteurX in range(len(clq)):
            for acteurY in range(len(clq)):
                if acteurX == acteurY or randEDG[clq[acteurX]][clq[acteurY]] > 19:
                    continue
                else:
                    randEDG[clq[acteurX]][clq[acteurY]] = random.randint(20, 90)
        clq.sort(key=None, reverse=False)
        clqs.append((clq, weightOfClique(randEDG, clq)))
    clqs.sort(key=lambda x: x[1], reverse=True)
    print('created cliques: ')
    for clique in range(len(clqs)):
        print(clique + 1, ': ', clqs[clique], len(clqs[clique][0]))
    return randEDG, clqs

# Funktion: Berechnet den degree-basierten Zentralitaetswert aller Akteure einer Clique. 
# Die Funktion dient in erster Linie dazu, fuer die Startclique die aussichtsreichsten 
# Kandidaten zu finden
# Rueckgabewert: Eine sortierte Liste mit den Akteuren und ihren Zentralitaetswerten
def calcCentrality(myArr):
    # Vectorized bidirectional check
    # Nur Akteure mit einem Zentralitaetswert >0 werden in die Liste aufgenommen. 
    # Ein Wert von Null bedeutet, dass der Akteur
    # mit keinem anderen Akteur bidirektional verbunden ist
    bidirectional = (myArr > 0) & (myArr.T > 0)
    # Remove diagonal
    np.fill_diagonal(bidirectional, False)
    # Count connections per actor
    degrees = np.sum(bidirectional, axis=1)
    # Filter actors with degree > 0
    valid_actors = np.where(degrees > 0)[0]
    # Create sorted list
    actSortByCent = sorted([(int(actor), int(degrees[actor])) 
                         for actor in valid_actors], 
                        key=lambda x: x[1], reverse=True)
    print('Number of acteurs with centrality > 0: ', len(actSortByCent))
    return actSortByCent

# Funktion: berechnet die Dichte eines Graphen
# die Angabe ist rein informativ, wird sonst nicht benutzt
# Rueckgabewert: Die Dichte des Graphen myArr
def calcDensity(myArr):
    """Calculate density using vectorized NumPy operations"""
    nrOfActors = myArr.shape[0]
    # Count all non-zero elements (edges)
    nrOfEdges = np.count_nonzero(myArr)
    # Calculate density
    density = nrOfEdges / (nrOfActors * (nrOfActors - 1))
    return round(density, 4)

# Funktion: Verarbeitet eine Liste von Elementen in zufaelliger Reihenfolge
def randrange(start, stop): 
    values = list(range(start, stop)) 
    random.shuffle(values) 
 
    while values: 
        yield values.pop() 

# Funktion: Findet eine moeglichst aussichtsreiche Start-Clique
# Rueckgabewert: Die Start-Clique
def initialClique(myArr, myActSortByCent, iterations, iterMax):
    """Find a promising starting clique using adaptive candidate selection"""
    nrOfCActors = len(myActSortByCent)
    nrOfActors = myArr.shape[0]
    randClique = []
    
    # Adaptive candidate selection: quadratic curve for initial clique
    actToCheck = calculate_initial_clique_range(iterations, iterMax, nrOfCActors)
    startActeur = random.randint(0, actToCheck - 1)
    a, b = myActSortByCent[startActeur]
    randClique.append(a)
    
    # Build clique by adding actors with bidirectional connections to all members
    for acteur in randrange(0, nrOfActors - 1):
        if len(randClique) == 0:
            randClique.append(acteur)
        elif acteur not in randClique:
            # Check bidirectional connections with all current clique members
            if all(is_bidirectional_connection(myArr, acteur, member) for member in randClique):
                randClique.append(acteur)
    
    return randClique

# Funktion: Berechnet die beiden Nachbarschaften ADD und SWAP und gibt die am 
# hoechsten bewerteten Cliquen sowie die Kandidaten fuer die Tabu-Listen zurueck
# Rueckgabewerte: 
#     bestCliqueAddCand, bestCliqueSwapCand: Jeweils der am besten geeignete Kandidat der beiden
#         Nachbarschaften
#     tabuADDCand, tabuSWAPCand, tabuSWAPADDCand: Die Kandidaten fuer die neuen Tabu-Listen
#     swapCandidates.__len__(): Die Anzahl der SWAP-Kandidaten. Wichtig, weil die Laenge der
#         Tabu-Liste dynamisch ist
def neighborhoodAddSwap(myArr, myClique, myActSortByCent, tabuDROPList, tabuSWAPList, iterations, iterMax):
    """Calculate ADD and SWAP neighborhoods using adaptive candidate selection"""
    bestCliqueAddCand = myClique[:]
    bestCliqueSwapCand = myClique[:]
    cliqueSize = len(myClique)
    
    # Initialize tabu candidates
    tabuADDCand = -1
    tabuSWAPCand = -1
    tabuSWAPADDCand = -1
    
    # Adaptive candidate selection based on algorithm progress (cubic curve)
    actToCheck = calculate_neighborhood_range(iterations, iterMax, len(myActSortByCent))
    
    # Find ADD and SWAP candidates
    addCandidates = []
    swapCandidates = []
    swapCandDict = {}
    
    for acteurPos in range(0, actToCheck):
        acteur, deg = myActSortByCent[acteurPos]
        
        # Skip actors already in clique or on tabu lists
        if acteur in myClique or acteur in tabuDROPList or acteur in tabuSWAPList:
            continue
        
        # Check connections with current clique members
        noConn = 0
        conn = 0
        cliqueMembertoSwap = None
        
        for cliqueMember in range(cliqueSize):
            if is_bidirectional_connection(myArr, acteur, myClique[cliqueMember]):
                conn = conn + 1
            else:
                noConn = noConn + 1
                if noConn > 1:
                    break  # More than one missing connection - not a candidate
                else:
                    cliqueMembertoSwap = myClique[cliqueMember]
        
        # Categorize candidate
        if conn == cliqueSize:
            addCandidates.append(acteur)
        elif noConn == 1:
            swapCandidates.append(acteur)
            swapCandDict[acteur] = cliqueMembertoSwap
    
    # Find best ADD candidate
    bestAddCandidate = find_best_add_candidate(myArr, addCandidates, bestCliqueAddCand)
    if bestAddCandidate is not None:
        bestCliqueAddCand.append(bestAddCandidate)
        tabuADDCand = bestAddCandidate
    else:
        bestCliqueAddCand = []
    
    # Find best SWAP candidate
    bestSwapCandidate, toRemove = find_best_swap_candidate(myArr, swapCandidates, swapCandDict, bestCliqueSwapCand)
    if bestSwapCandidate is not None:
        bestCliqueSwapCand.remove(toRemove)
        bestCliqueSwapCand.append(bestSwapCandidate)
        tabuSWAPCand = toRemove
        tabuSWAPADDCand = bestSwapCandidate
    else:
        bestCliqueSwapCand = []
        swapCandidates = []
    
    return bestCliqueAddCand, bestCliqueSwapCand, tabuADDCand, tabuSWAPCand, tabuSWAPADDCand, len(swapCandidates)

# Funktion: berechnet die Nachbarschaft DROP: Sucht denjenigen Kandidaten, welcher 
# mit dem geringsten Verlust entfernt werden kann
# Rueckgabewerte: 
#     bestCliqueDropCand: Der an besten geeignete Kandidat 
#     tabuCand: Der Kandidat fuer die neue Tabu-Liste
def neighborhoodDrop(myArr, myClique, tabuADDList):
    tabuCand = -1
    candDrop = -1
    bestCliqueDropCand = myClique[:]
    if len(myClique) > 2:
        minNegSum = weightOfClique(myArr, bestCliqueDropCand)
        for testCand in randrange(0, len(bestCliqueDropCand) - 1):
            negSum = 0
            if bestCliqueDropCand[testCand] not in tabuADDList:
                for testCandCompare in range(len(bestCliqueDropCand)):
                    if testCand == testCandCompare:
                        continue
                    else:
                        negSum += myArr[bestCliqueDropCand[testCand]][bestCliqueDropCand[testCandCompare]] + myArr[bestCliqueDropCand[testCandCompare]][bestCliqueDropCand[testCand]]
                if negSum < minNegSum:
                    minNegSum = negSum
                    candDrop = testCand
        if candDrop != -1:
            bestDropCandidate = bestCliqueDropCand[candDrop]
            bestCliqueDropCand.remove(bestDropCandidate)
            tabuCand = bestDropCandidate
    else:
        bestCliqueDropCand = []
    return bestCliqueDropCand, tabuCand

# Funktion: Die Berechnung des Wertes einer Clique; setzt sich zusammen aus der Laenge 
# und der Summe der Kantengewichte zwischen den Mitgliedern der Clique 
# Rueckgabewert: Der Wert der Clique
def weightOfClique(myArr, myClique):
    cliqueValue = 0
    if len(myClique) > 0:
        for acteurX in range(len(myClique)):
            for acteurY in range(len(myClique)):
                if acteurX == acteurY:
                    continue
                else:
                    cliqueValue = cliqueValue + int(myArr[myClique[acteurX]][myClique[acteurY]])
        weight = int(cliqueValue)  # Convert to Python int
    else:
        weight = 0
    return weight

# Funktion: prueft, ob eine Clique als Sub-Clique einer Liste von Cliquen vorkommt
# Rueckgabewert: False, wenn die Clique keine Sub-Clique ist
def subClq(bestClqCand, bestCliques):
    clqCand = bestClqCand[0]
    for clqs in range(len(bestCliques)):
        if bestClqCand == bestCliques[clqs]:
            continue
        clq = (bestCliques[clqs])[0]
        noSubClique = 0
        for i in range(len(clqCand)):
            if clqCand[i] not in clq:
                noSubClique = 1
                break
        if noSubClique == 0:
            return True
    return False

def calculate_add_score(myArr, candidate, current_clique):
    """Calculate total bidirectional weight for ADD candidate"""
    return sum(myArr[candidate][member] + myArr[member][candidate] 
               for member in current_clique)

def calculate_swap_score(myArr, candidate, to_remove, current_clique):
    """Calculate net gain for SWAP operation (gain - loss) - matches original algorithm"""
    gain = sum(myArr[candidate][member] + myArr[member][candidate] 
               for member in current_clique)
    loss = sum(myArr[to_remove][member] + myArr[member][to_remove] 
               for member in current_clique if member != to_remove)
    return gain - loss

def calculate_initial_clique_range(iterations, iter_max, total_actors):
    """Calculate adaptive range for initial clique (quadratic curve)"""
    mult = (iterations / iter_max) ** 2  # Quadratic curve for initial clique
    range_val = int(total_actors / 100 * (mult * 99 + 1)) + 1  # Original had +1
    return min(range_val, total_actors)

def calculate_neighborhood_range(iterations, iter_max, total_actors):
    """Calculate adaptive range for neighborhood operations (cubic curve)"""
    mult = (iterations / iter_max) ** 3 + 0.4  # Cubic curve + offset for neighborhood
    range_val = int(total_actors / 100 * (mult * 99 + 1))
    return min(range_val, total_actors)

def calculate_adaptive_range(iterations, iter_max, total_actors):
    """Calculate adaptive candidate range based on progress (empirically tuned)"""
    mult = (iterations / iter_max) ** 3 + 0.4  # Empirical study result
    range_val = int(total_actors / 100 * (mult * 99 + 1))
    return min(range_val, total_actors)  # Ensure we don't exceed array bounds

def is_bidirectional_connection(myArr, actor1, actor2):
    """Check if both directions have non-zero connections (key algorithm requirement)"""
    return myArr[actor1][actor2] > 0 and myArr[actor2][actor1] > 0

def calculate_swap_tabu_length(swap_candidates_count):
    """Calculate dynamic tabu list length based on scientific paper"""
    return random.randint(1, swap_candidates_count) + 7

def find_best_add_candidate(myArr, add_candidates, current_clique):
    """Find the best ADD candidate based on total bidirectional weight"""
    if not add_candidates:
        return None
    
    best_candidate = None
    max_score = -1
    
    for candidate in add_candidates:
        score = calculate_add_score(myArr, candidate, current_clique)
        if score > max_score:
            max_score = score
            best_candidate = candidate
    
    return best_candidate

def find_best_swap_candidate(myArr, swap_candidates, swap_dict, current_clique):
    """Find the best SWAP candidate based on net gain calculation"""
    if not swap_candidates or len(current_clique) <= 1:
        return None, None
    
    best_candidate = None
    best_to_remove = None
    max_net_gain = -sys.maxsize
    
    for candidate in swap_candidates:
        to_remove = swap_dict[candidate]
        net_gain = calculate_swap_score(myArr, candidate, to_remove, current_clique)
        if net_gain > max_net_gain:
            max_net_gain = net_gain
            best_candidate = candidate
            best_to_remove = to_remove
    
    return best_candidate, best_to_remove

def update_best_cliques(myArr, bestCliques, localBestClique, nrOfCliques, iterations, passedTime):
    """Update the best cliques list with new candidate and remove subcliques"""
    if len(localBestClique) > 2:
        bestClqCand = ((localBestClique, weightOfClique(myArr, localBestClique), iterations, passedTime))
        if (bestClqCand not in bestCliques and 
            (len(bestCliques) < (nrOfCliques + 1) or 
             weightOfClique(myArr, localBestClique) >= weightOfClique(myArr, bestCliques[0][0]))):
            if not subClq(bestClqCand, bestCliques):
                bestCliques.append(bestClqCand)
                bestCliques.sort(key=lambda x: x[1], reverse=False)
                # Remove subcliques of the new clique
                bestCliquesTemp = bestCliques[:]
                if len(bestCliques) > 1:
                    for clqs in range(0, len(bestCliques) - 1):
                        clq = bestCliques[clqs]
                        if subClq(clq, bestCliques):
                            bestCliquesTemp.remove(clq)
                bestCliques = bestCliquesTemp[:]
                if len(bestCliques) > nrOfCliques:
                    bestCliques.pop(0)
    return bestCliques

def select_best_neighbor(myArr, currentClique, myActSortByCent, tabuDROPList, tabuSWAPList, tabuADDList, tabuADDlength, tabuDROPlength, iterations, iterMax):
    """Select the best neighborhood operation (ADD, DROP, or SWAP)"""
    # Calculate neighborhoods
    bestAddCliqueCand, bestSwapCliqueCand, tabuADDCand, tabuSWAPCand, tabuSWAPADDCand, nrOfSWAPCand = neighborhoodAddSwap(
        myArr, currentClique, myActSortByCent, tabuDROPList, tabuSWAPList, iterations, iterMax)
    
    # Calculate DROP neighborhood
    bestDropCliqueCand, tabuDropCand = neighborhoodDrop(myArr, currentClique, tabuADDList)
    
    # Select best option
    addWeight = weightOfClique(myArr, bestAddCliqueCand) if len(bestAddCliqueCand) > 0 else -1
    swapWeight = weightOfClique(myArr, bestSwapCliqueCand) if len(bestSwapCliqueCand) > 0 else -1
    dropWeight = weightOfClique(myArr, bestDropCliqueCand) if len(bestDropCliqueCand) > 0 else -1
    
    if addWeight > swapWeight and addWeight > dropWeight:
        # ADD selected
        bestNeighborClique = bestAddCliqueCand[:]
        manage_tabu_list(tabuADDList, tabuADDlength, tabuADDCand)
        return bestNeighborClique
    elif dropWeight > swapWeight and dropWeight > addWeight:
        # DROP selected
        bestNeighborClique = bestDropCliqueCand[:]
        manage_tabu_list(tabuDROPList, tabuDROPlength, tabuDropCand)
        return bestNeighborClique
    elif len(bestSwapCliqueCand) > 0 and swapWeight > addWeight and swapWeight > dropWeight:
        # SWAP selected
        bestNeighborClique = bestSwapCliqueCand[:]
        manage_swap_tabu_list(tabuSWAPList, nrOfSWAPCand)
        manage_tabu_list(tabuADDList, tabuADDlength, tabuSWAPADDCand)
        tabuSWAPList.append(tabuSWAPCand)
        return bestNeighborClique
    else:
        # No valid neighbor found
        return []

def manage_swap_tabu_list(tabuSWAPList, nrOfSWAPCand):
    """Manage SWAP tabu list with dynamic length based on scientific paper"""
    tabuSWAPListlength = calculate_swap_tabu_length(nrOfSWAPCand)
    while len(tabuSWAPList) > tabuSWAPListlength:
        tabuSWAPList.pop(0)  # Remove oldest (FIFO)
    return tabuSWAPListlength

def manage_tabu_list(tabuList, maxLength, newItem):
    """Manage a FIFO tabu list with fixed maximum length"""
    if len(tabuList) >= maxLength:
        tabuList.pop(0)  # Remove oldest item (FIFO)
    tabuList.append(newItem)  # Add new item

def report_progress(iterations, iterMax, steps):
    """Report progress percentage at specified intervals"""
    if iterations % steps == 0 and iterations <= iterMax:
        completed = round(float(iterations) / iterMax * 100, 0)
        if completed > 100:
            completed = 100.0
        print(completed, '% completed')

# Funktion: Der neue MN/TS for EDG Algorithmus
# Rueckgabewert: Eine Menge von Cliquen
def MultiTabuSearch(myArr, iterMax, searchDepth, nrOfCliques):
    tabuADDlength = 2
    tabuDROPlength = 7
    iterations = 0
    if iterMax > 9:
        steps = int(iterMax // 10)
    else:
        steps = 1
    maxClique = np.int_([])
    bestCliques = []
    print('...sorting acteurs by centrality (can take some minutes)...')
    time12 = time.perf_counter()
    myActSortByCent = calcCentrality(myArr)
    time13 = time.perf_counter()
    tt = time13 - time12
    print('time to sort', len(myActSortByCent), 'acteurs by centrality: ', tt)
    startTime = time.perf_counter()
    print('...start iterations...')
    while iterations < iterMax:
        currentClique = initialClique(myArr, myActSortByCent, iterations, iterMax)
        currentClique.sort(key=None, reverse=False)
        tabuADDList = []
        tabuSWAPList = []
        tabuDROPList = []
        notImproved = 0
        if len(currentClique) == 1:
            notImproved = searchDepth
        else:
            localBestClique = currentClique[:]
        while notImproved < searchDepth:
            bestNeighborClique = select_best_neighbor(myArr, currentClique, myActSortByCent, 
                                                     tabuDROPList, tabuSWAPList, tabuADDList, 
                                                     tabuADDlength, tabuDROPlength, iterations, iterMax)
            
            if len(bestNeighborClique) > 0:
                currentClique = bestNeighborClique[:]
                currentClique.sort(key=None, reverse=False)
            notImproved = notImproved + 1
            iterations = iterations + 1
            report_progress(iterations, iterMax, steps)
            if weightOfClique(myArr, currentClique) > weightOfClique(myArr, localBestClique):
                notImproved = 0
                localBestClique = currentClique[:]
        if searchDepth == 0:
            iterations = iterations + 1
            report_progress(iterations, iterMax, steps)
        actTime = time.perf_counter()
        passedTime = actTime - startTime
        bestCliques = update_best_cliques(myArr, bestCliques, localBestClique, nrOfCliques, iterations, passedTime)
        if weightOfClique(myArr, localBestClique) > weightOfClique(myArr, maxClique):                
            maxClique = localBestClique[:]
    return bestCliques




parser = optparse.OptionParser(version="%prog 1.0")
parser.add_option("-f", "--dimacs", dest="dimacsFilename", default="", help="DIMACS file to load", metavar="FILE")
parser.add_option("-s", "--sample", dest="sampleSize", type="int", default=0, help="creates a sample network of size SAMPLESIZE with cliques - minimum size = 10; maximum size = 22000")
parser.add_option("-i", "--iterations", dest="iter", type="int", default=0, help="defines the number of iterations")
parser.add_option("-d", "--depth", dest="depth", type="int", default= -1, help="defines the search depth (0 means no local search)")
parser.add_option("-o", "--out", dest="outFilename", default="", help="name of the output file (adjacency matrix) in csv format")
parser.add_option("-c", "--in", dest="inFilename", default="", help="name of the input file (adjacency matrix) in csv format")
parser.add_option("-n", "--cliques", dest="nrOfCliques", type="int", default=10, help="number of cliques to find - default is 10")
(options, args) = parser.parse_args()

print('options: ', options)
print('args: ', args)

# Behandlung Eingabefehler
# Anzahl zu findender Cliquen kleiner als 1
if options.nrOfCliques < 1:
    print("the number of cliques to find must be > 0")
    exit(-1)

# Behandlung Eingabefehler
# Die Suchtiefe ist groesser als die Anzahl Iterationen
if options.depth > options.iter:
    print("search depth > number of iterations doesn't make sense")
    exit(-1)    

# Behandlung Eingabefehler
# Die Anzahl Iterationen fehlt oder ist kleiner als 1    
if options.iter < 1:
    print("please specify number of iterations")
    exit(-1)
else:
    iter = options.iter

# Behandlung Eingabefehler
# Die Suchtiefe ist kleiner als 0
# (Suchtiefe = 0 heisst, dass der Local Search Teil des Algorithmus ausgelassen wird)    
if options.depth < 0:
    print("please specify the search depth")
    exit(-1)
else:
    depth = options.depth

# Behandlung Eingabefehler
# Es soll gleichzeitig ein Netzwerk simuliert und ein File eingelesen werden
if options.sampleSize != 0 and (options.dimacsFilename != "" or options.inFilename != ""):
    print("you can't specify a filename AND create a sample network")
    exit(-1)

# Behandlung Eingabefehler
# Es soll eine DIMACS- UND eine CSV-Datei eingelesen werden
if options.dimacsFilename != "" and options.inFilename != "":
    print("you can't specify a dimacs filename AND a csv filename")
    exit(-1)

# Behandlung Eingabefehler
# Es soll weder ein Netzwerk simuliert noch eine Datei eingelesen werden
if options.dimacsFilename == "" and options.inFilename == "" and options.sampleSize == 0:
    print("please specify either a dimacs filename, a csv filename or the size of a sample network")
    exit(-1)

# Ein Netzwerk soll simuliert und untersucht werden
if options.sampleSize != 0 and (options.dimacsFilename == "" and options.inFilename == ""):
    if options.sampleSize < 0:
        print("please enter a positive number as the amount of vertices")
        exit(-1)
    if options.sampleSize > 22000:
        print("not enough memory for such a large network")
        exit(-1)
    if options.sampleSize < 10:
        print("minimum number of acteurs is 10")
        exit(-1) 
    print('...creating array...')
    myMirrAdj, clqs = createSampleEDG(options.sampleSize)
    print('...created...')
    if options.outFilename != "":
        print("...writing to file...")
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        writeFile(clqs, filename + '.cliques')
        print('written to file: ', filename)

# Ein DIMACS-Graph soll untersucht werden
if options.sampleSize == 0 and (options.dimacsFilename != "" and options.inFilename == ""):
    filename = options.dimacsFilename
    print("reading array from", filename, "...")
    myAdj = read_DIMACS_graph(filename)
    myMirrAdj = mirror(myAdj)
    if not sizeOk(myMirrAdj):
        print("size of network must be between 10 and 22000")
        exit(-1)   
    if options.outFilename != "":
        print("...writing to file...")
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        print('written to file: ', filename)

# Ein CSV-File soll untersucht werden
if options.sampleSize == 0 and (options.dimacsFilename == "" and options.inFilename != ""):
    filename = options.inFilename
    print("reading array from", filename, "...")
    myMirrAdj = readFile_fast(filename)    
    if not sizeOk(myMirrAdj):
        print("size of network must be between 10 and 22000")
        exit(-1)  
    if options.outFilename != "":
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        print('written to file: ', filename)

logging.basicConfig(filename='MNTS_EDG.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.info('***  START ***')

for multEDG in range(1):

    print('...calculating density (can take some minutes)...')
    time7 = time.perf_counter()
    print('Density: ', calcDensity(myMirrAdj))
    time8 = time.perf_counter()
    tt = str(time8 - time7)
    print('time to calculate density: ', tt)
    print('...start finding cliques...')
    time5 = time.perf_counter()
    myDIMACSClique = MultiTabuSearch(myMirrAdj, iter, depth, options.nrOfCliques)
    time6 = time.perf_counter()
    tt = str(time6 - time5)
    print('time to find cliques: ', tt)
    logging.info('time to find cliques: %s', tt)
    myDIMACSClique.reverse()
    print('*** Clique - Weight - Iteration - Time - Size ***')
    print('The', len(myDIMACSClique), 'best Cliques: ')
    for clique in range(len(myDIMACSClique)):
        print(clique + 1, ': ', myDIMACSClique[clique], len(myDIMACSClique[clique][0]))

print('the end')
logging.info('***  END ***')
