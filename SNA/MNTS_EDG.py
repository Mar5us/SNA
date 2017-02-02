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
            f = gzip.open(filename, "rb")
        else:   # usual, uncompressed file
            f = open(filename)
    except IOError:
        print "could not open file", filename
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
            print "the file", filename,"is not in DIMACS format"
            exit(-1)
    f.close()
    return myArr

# Funktion: Fuellt ein Array mit Nullen
# Rueckgabewert: Das mit Nullen gefuellte Array
def initialize(size):
    myArr = np.int_([[0] * size for i in range(size)])
    return myArr

# Funktion: Fuellt ein Array einer bestimmten Dichte mit Zufallswerten
# Rueckgabewert: Das gefuellte Array
def fillRandomAdv(myArr, density):
    nrOfActors = myArr.shape[0]
    nrofEdgesPerVertex = float((nrOfActors - 1) * density)
    randVal1 = random.randint(80, 100)
    iMax = int(nrOfActors / 100 * randVal1)
    i = 0
    for acteur in randrange(0, nrOfActors - 1):
        i = i + 1
        if (i > iMax):
            break  
        nrofEdgesPerVertexRandom = random.randint(int(nrofEdgesPerVertex - nrofEdgesPerVertex / 5), int(nrofEdgesPerVertex + nrofEdgesPerVertex / 5))
        for contacts in range(int(nrofEdgesPerVertexRandom / 2)):
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
        print i, ': ',
        for j in range(nrOfActors):
            print myArr[i][j],
        print ''

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
        print "could not open file", filename
        exit(-1) 
    return newArr

# Funktion: Schreibt ein Array in ein CSV-File
def writeFile(myArr, filename):
    f = open(filename, "wb")
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
    if ((size > 100) and (size <= 10000)):
        density = 0.01
    if ((size > 10000) and (size <= 20000)):
        density = 0.005
    if (size > 20000):
        density = 0.001
    randEDG = fillRandomAdv(edg, density)
    clqs = []
    for randCLQ in range(nrOfCliques):
        clq = []
        if (size <= 100):
            clqlength = 4
        else:
            clqlength = random.randint(4, size / 400 + 10) 
        while (clq.__len__() < clqlength):
            member = random.randint(0, size - 1)
            if (not clq.__contains__(member)):
                clq.append(member)
        for acteurX in range(clq.__len__()):
            for acteurY in range(clq.__len__()):
                if ((acteurX == acteurY) or (randEDG[clq[acteurX]][clq[acteurY]] > 19)):
                    continue
                else:
                    randEDG[clq[acteurX]][clq[acteurY]] = random.randint(20, 90)
        clq.sort(cmp=None, key=None, reverse=False)
        clqs.append((clq, weightOfClique(randEDG, clq)))
    clqs.sort(cmp=None, key=lambda x: x[1], reverse=True)
    print 'created cliques: '
    for clique in range(clqs.__len__()):
        print clique + 1, ': ', clqs[clique], clqs[clique][0].__len__()
    return randEDG, clqs

# Funktion: Berechnet den degree-basierten Zentralitaetswert aller Akteure einer Clique. 
# Die Funktion dient in erster Linie dazu, fuer die Startclique die aussichtsreichsten 
# Kandidaten zu finden
# Rueckgabewert: Eine sortierte Liste mit den Akteuren und ihren Zentralitaetswerten
def calcCentrality(myArr):
    nrOfActors = myArr.shape[0]
    degree = []
    for acteurX in range(nrOfActors):
        deg = 0
        for acteurY in range(nrOfActors):
            if (acteurX == acteurY):
                continue
            else:
                if ((myArr[acteurY][acteurX] > 0) and (myArr[acteurX][acteurY] > 0)):
                    deg = deg + 1
        if (deg > 0): 
            degree.append((acteurX, deg))
            # Nur Akteure mit einem Zentralitaetswert >0 werden in die Liste aufgenommen. 
            # Ein Wert von Null bedeutet, dass der Akteur
            # mit keinem anderen Akteur bidirektional verbunden ist
    actSortByCent = sorted(degree, key=lambda x: x[1], reverse=True)
    print 'Number of acteurs with centrality > 0: ', actSortByCent.__len__()
    return actSortByCent

# Funktion: berechnet die Dichte eines Graphen
# die Angabe ist rein informativ, wird sonst nicht benutzt
# Rueckgabewert: Die Dichte des Graphen myArr
def calcDensity(myArr):
    nrOfActors = myArr.shape[0]
    nrOfEdges = 0
    for i in range(nrOfActors):
        for j in range(nrOfActors):
            if (myArr[i][j] > 0):
                nrOfEdges = nrOfEdges + 1
    density = round(float(nrOfEdges) / (nrOfActors * (nrOfActors - 1)), 4)
    return density

# Funktion: Verarbeitet eine Liste von Elementen in zufaelliger Reihenfolge
def randrange(start, stop): 
    values = range(start, stop) 
    random.shuffle(values) 
 
    while values: 
        yield values.pop() 
 
    raise StopIteration 

# Funktion: Findet eine moeglichst aussichtsreiche Start-Clique
# Rueckgabewert: Die Start-Clique
def initialClique(myArr, myActSortByCent, iterations, iterMax):
    nrOfCActors = myActSortByCent.__len__()
    nrOfActors = myArr.shape[0]
    randClique = []
    mult = (float(iterations) / float(iterMax)) ** 2 # ergibt eine nichtlineare Kurve
    # Der Range der moeglichen Kandidaten fuer die Startclique vergroessert sich mit der Zeit
    actToCheck = int((float(nrOfCActors)) / 100 * (mult * 99 + 1)) + 1
    startActeur = random.randint(0, actToCheck - 1)
    a, b = myActSortByCent[startActeur]
    # Der erste Akteur der Startclique soll einer mit einem moeglichst hohen Centrality-Wert sein
    randClique.append(a)
    
    for acteur in randrange(0, nrOfActors - 1):
        if (randClique.__len__() == 0):
            randClique.append(acteur)
        else:
            if randClique.__contains__(acteur):
                continue          
            flag = 0
            for j in range(randClique.__len__()):
                # auf Gegenseitigkeit pruefen
                if ((myArr[randClique[j]][acteur] == 0) or (myArr[acteur][randClique[j]] == 0)):
                    flag = 0
                    break
                else:
                    flag = 1
            if (flag == 1):
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
    bestCliqueAddCand = myClique[:]
    bestCliqueSwapCand = myClique[:]
    nrOfActorsPos = myActSortByCent.__len__()
    cliqueSize = myClique.__len__()
    tabuADDCand = -1
    tabuSWAPCand = -1
    tabuSWAPADDCand = -1
    swapCandDict = {}
    addCandidates = []
    swapCandidates = []
    mult = ((float(iterations) / float(iterMax)) ** 3) + 0.4 #ergibt eine nichtlineare Kurve
    if (mult > 1):
        mult = 1
    actToCheck = int((float(nrOfActorsPos)) / 100 * (mult * 99 + 1))
    for acteurPos in range(0, actToCheck):
        acteur, deg = myActSortByCent[acteurPos]
        noConn = 0
        conn = 0
        if ((myClique.__contains__(acteur)) or (tabuDROPList.__contains__(acteur)) or (tabuSWAPList.__contains__(acteur))):
            continue
        for cliqueMember in range(cliqueSize):
            if ((myArr[acteur][myClique[cliqueMember]] > 0) and (myArr[myClique[cliqueMember]][acteur] > 0)):
                conn = conn + 1
            else:
                noConn = noConn + 1
                if (noConn > 1):
                    break
                else:
                    cliqueMembertoSwap = myClique[cliqueMember]
        if (conn == cliqueSize):
            addCandidates.append(acteur)
        else:
            if (noConn == 1):
                swapCandidates.append(acteur)
                swapCandDict.update({acteur: cliqueMembertoSwap})

    if (addCandidates.__len__() > 0):
        addSum = 0
        maxAddSum = 0
        for testCand in range(addCandidates.__len__()):
            for testCandCompare in range(bestCliqueAddCand.__len__()):
                addSum = addSum + myArr[addCandidates[testCand]][bestCliqueAddCand[testCandCompare]] + myArr[bestCliqueAddCand[testCandCompare]][addCandidates[testCand]]
            if (addSum > maxAddSum):
                maxAddSum = addSum
                candAdd = testCand
        bestAddCandidate = addCandidates[candAdd]
        bestCliqueAddCand.append(bestAddCandidate)
        tabuADDCand = bestAddCandidate
    else:
        bestCliqueAddCand = []
     
    if ((swapCandidates.__len__() > 0) and (cliqueSize > 1)):
        swapSum = 0
        swapNeg = 0
        maxSWAPDiff = -sys.maxint
        for testCand in range(swapCandidates.__len__()):
            candToSwap = swapCandDict[swapCandidates[testCand]]
            for testCandCompare in range(bestCliqueSwapCand.__len__()):
                swapSum = swapSum + myArr[swapCandidates[testCand]][bestCliqueSwapCand[testCandCompare]] + myArr[bestCliqueSwapCand[testCandCompare]][swapCandidates[testCand]]
                if (candToSwap == bestCliqueSwapCand[testCandCompare]):
                    continue
                else:
                    swapNeg = swapNeg + myArr[candToSwap][bestCliqueSwapCand[testCandCompare]] + myArr[bestCliqueSwapCand[testCandCompare]][candToSwap]
                    swapDiff = swapSum - swapNeg
            if (swapDiff > maxSWAPDiff):
                maxSWAPDiff = swapDiff
                candSwap = testCand            
        bestSwapCandidate = swapCandidates[candSwap]
        bestCliqueSwapCand.remove(swapCandDict[bestSwapCandidate])
        bestCliqueSwapCand.append(bestSwapCandidate)        
        tabuSWAPCand = swapCandDict[bestSwapCandidate]
        tabuSWAPADDCand = bestSwapCandidate
        
    else:
        bestCliqueSwapCand = []
        swapCandidates = []               
    
    return bestCliqueAddCand, bestCliqueSwapCand, tabuADDCand, tabuSWAPCand, tabuSWAPADDCand, swapCandidates.__len__()

# Funktion: berechnet die Nachbarschaft DROP: Sucht denjenigen Kandidaten, welcher 
# mit dem geringsten Verlust entfernt werden kann
# Rueckgabewerte: 
#     bestCliqueDropCand: Der an besten geeignete Kandidat 
#     tabuCand: Der Kandidat fuer die neue Tabu-Liste
def neighborhoodDrop(myArr, myClique, tabuADDList):
    tabuCand = -1
    candDrop = -1
    bestCliqueDropCand = myClique[:]
    if (myClique.__len__() > 2):
        minNegSum = weightOfClique(myArr, bestCliqueDropCand)
        for testCand in randrange(0, bestCliqueDropCand.__len__() - 1):
            negSum = 0
            if (not (tabuADDList.__contains__(bestCliqueDropCand[testCand]))):
                for testCandCompare in range(bestCliqueDropCand.__len__()):
                    if (testCand == testCandCompare):
                        continue
                    else:
                        negSum = negSum + myArr[bestCliqueDropCand[testCand]][bestCliqueDropCand[testCandCompare]] + myArr[bestCliqueDropCand[testCandCompare]][bestCliqueDropCand[testCand]]
                if (negSum < minNegSum):
                    minNegSum = negSum
                    candDrop = testCand
        if (candDrop <> -1):
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
    if (myClique.__len__() > 0):
        for acteurX in range(myClique.__len__()):
            for acteurY in range(myClique.__len__()):
                if (acteurX == acteurY):
                    continue
                else:
                    cliqueValue = cliqueValue + myArr[myClique[acteurX]][myClique[acteurY]]
        weight = cliqueValue
    else:
        weight = 0
    return weight

# Funktion: prueft, ob eine Clique als Sub-Clique einer Liste von Cliquen vorkommt
# Rueckgabewert: False, wenn die Clique keine Sub-Clique ist
def subClq(bestClqCand, bestCliques):
    clqCand = bestClqCand[0]
    for clqs in range(bestCliques.__len__()):
        if (bestClqCand == bestCliques[clqs]):
            continue
        clq = (bestCliques[clqs])[0]
        noSubClique = 0
        for i in range(clqCand.__len__()):
            if (not (clq.__contains__(clqCand[i]))):
                noSubClique = 1
                break
        if (noSubClique == 0):
            return True
    return False

# Funktion: Der neue MN/TS for EDG Algorithmus
# Rueckgabewert: Eine Menge von Cliquen
def MultiTabuSearch(myArr, iterMax, searchDepth, nrOfCliques):
    tabuADDlength = 2
    tabuDROPlength = 7
    iterations = 0
    if (iterMax > 9):
        steps = int(iterMax / 10)
    else:
        steps = 1
    maxClique = np.int_([])
    bestCliques = []
    print '...sorting acteurs by centrality (can take some minutes)...'
    time12 = time.clock()
    myActSortByCent = calcCentrality(myArr)
    time13 = time.clock()
    tt = time13 - time12
    print 'time to sort', myActSortByCent.__len__(), 'acteurs by centrality: ', tt
    startTime = time.clock()
    print '...start iterations...'
    while (iterations < iterMax):
        currentClique = initialClique(myArr, myActSortByCent, iterations, iterMax)
        currentClique.sort(cmp=None, key=None, reverse=False)
        tabuADDList = []
        tabuSWAPList = []
        tabuDROPList = []
        notImproved = 0
        if (currentClique.__len__() == 1):
            notImproved = searchDepth
        else:
            localBestClique = currentClique[:]
        while (notImproved < searchDepth):
            bestNeighborClique = []
            # berechnet die Nachbarschaften ADD und SWAP
            bestAddCliqueCand, bestSwapCliqueCand, tabuADDCand, tabuSWAPCand, tabuSWAPADDCand, nrOfSWAPCand = neighborhoodAddSwap(myArr, currentClique, myActSortByCent, tabuDROPList, tabuSWAPList, iterations, iterMax)
            # Nachbarschaft ADD auswaehlen, wenn vorhanden und groesser als SWAP Nachbarschaft
            if ((bestAddCliqueCand.__len__() > 0) and (weightOfClique(myArr, bestAddCliqueCand) > weightOfClique(myArr, bestSwapCliqueCand))): 
                # Nachbarschaft ADD auswaehlen
                bestNeighborClique = bestAddCliqueCand[:]
                # Tabu ADD Liste nachfuehren
                if (tabuADDList.__len__() >= tabuADDlength):
                    tabuADDList.pop(0) # mit append und pop(0) wird eine FIFO Liste implementiert
                tabuADDList.append(tabuADDCand)
            else:
                # berechnet die Nachbarschaft DROP und vergleicht sie mit der SWAP Nachbarschaft
                bestDropCliqueCand, tabuDropCand = neighborhoodDrop(myArr, currentClique, tabuADDList)
                if (weightOfClique(myArr, bestDropCliqueCand) > weightOfClique(myArr, bestSwapCliqueCand)):
                    # Nachbarschaft DROP auswaehlen
                    bestNeighborClique = bestDropCliqueCand[:]
                    # Tabu DROP Liste nachfuehren
                    if (tabuDROPList.__len__() >= tabuDROPlength):
                        tabuDROPList.pop(0) # mit append und pop(0) wird eine FIFO Liste implementiert
                    tabuDROPList.append(tabuDropCand)
                else:
                    if (bestSwapCliqueCand.__len__() > 0):
                        # Nachbarschaft SWAP auswaehlen
                        bestNeighborClique = bestSwapCliqueCand[:]
                        # Tabu SWAP Liste nachfuehren
                        tabuSWAPListlength = random.randint(1, nrOfSWAPCand) + 7
                        while (tabuSWAPList.__len__() > tabuSWAPListlength):
                            tabuSWAPList.pop(0) # mit append und pop(0) wird eine FIFO Liste implementiert
                        # Tabu ADD Liste nachfuehren
                        if (tabuADDList.__len__() >= tabuADDlength):
                            tabuADDList.pop(0) # mit append und pop(0) wird eine FIFO Liste implementiert
                        tabuADDList.append(tabuSWAPADDCand)
                        tabuSWAPList.append(tabuSWAPCand)
            
            if (bestNeighborClique.__len__() > 0):
                currentClique = bestNeighborClique[:]
                currentClique.sort(cmp=None, key=None, reverse=False)
            notImproved = notImproved + 1
            iterations = iterations + 1
            if ((iterations % steps) == 0 and (iterations <= iterMax)):
                completed = round(float(iterations) / iterMax * 100, 0)
                if (completed > 100):
                    completed = 100.0
                print completed, '% completed'
            if (weightOfClique(myArr, currentClique) > weightOfClique(myArr, localBestClique)):
                notImproved = 0
                localBestClique = currentClique[:]
        if (searchDepth == 0):
            iterations = iterations + 1
            if ((iterations % steps) == 0 and (iterations <= iterMax)):
                completed = round(float(iterations) / iterMax * 100, 0)
                if (completed > 100):
                    completed = 100
                print completed, '% completed'
        actTime = time.clock()
        passedTime = actTime - startTime
        if (localBestClique.__len__() > 2):
            bestClqCand = ((localBestClique, weightOfClique(myArr, localBestClique), iterations, passedTime))
            if ((not bestCliques.__contains__(bestClqCand)) and ((bestCliques.__len__() < (nrOfCliques + 1)) or (weightOfClique(myArr, localBestClique) >= weightOfClique(myArr, bestCliques[0])))):
                if (not subClq(bestClqCand, bestCliques)):
                    bestCliques.append(bestClqCand)
                    bestCliques.sort(cmp=None, key=lambda x: x[1], reverse=False)
                    # prueft ob bereits gefundene Cliquen Subcliquen der neuen Clique sind.
                    bestCliquesTemp = bestCliques[:]
                    if (bestCliques.__len__() > 1):
                        for clqs in range(0, bestCliques.__len__() - 1):
                            clq = bestCliques[clqs]
                            if (subClq(clq, bestCliques)):
                                bestCliquesTemp.remove(clq)
                    bestCliques = bestCliquesTemp[:]
                    if (bestCliques.__len__() > nrOfCliques):
                        bestCliques.pop(0)
        if (weightOfClique(myArr, localBestClique) > weightOfClique(myArr, maxClique)):                
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

print 'options: ', options
print 'args: ', args

# Behandlung Eingabefehler
# Anzahl zu findender Cliquen kleiner als 1
if (options.nrOfCliques < 1):
    print "the number of cliques to find must be > 0"
    exit(-1)

# Behandlung Eingabefehler
# Die Suchtiefe ist groesser als die Anzahl Iterationen
if (options.depth > options.iter):
    print "search depth > number of iterations doesn't make sense"
    exit(-1)    

# Behandlung Eingabefehler
# Die Anzahl Iterationen fehlt oder ist kleiner als 1    
if (options.iter < 1):
    print "please specify number of iterations"
    exit(-1)
else:
    iter = options.iter

# Behandlung Eingabefehler
# Die Suchtiefe ist kleiner als 0
# (Suchtiefe = 0 heisst, dass der Local Search Teil des Algorithmus ausgelassen wird)    
if (options.depth < 0):
    print "please specify the search depth"
    exit(-1)
else:
    depth = options.depth

# Behandlung Eingabefehler
# Es soll gleichzeitig ein Netzwerk simuliert und ein File eingelesen werden
if ((options.sampleSize <> 0) and ((options.dimacsFilename <> "") or (options.inFilename <> ""))):
    print "you can't specify a filename AND create a sample network"
    exit(-1)

# Behandlung Eingabefehler
# Es soll eine DIMACS- UND eine CSV-Datei eingelesen werden
if ((options.dimacsFilename <> "") and (options.inFilename <> "")):
    print "you can't specify a dimacs filename AND a csv filename"
    exit(-1)

# Behandlung Eingabefehler
# Es soll weder ein Netzwerk simuliert noch eine Datei eingelesen werden
if ((options.dimacsFilename == "") and (options.inFilename == "") and options.sampleSize == 0):
    print "please specify either a dimacs filename, a csv filename or the size of a sample network"
    exit(-1)

# Ein Netzwerk soll simuliert und untersucht werden
if ((options.sampleSize <> 0) and ((options.dimacsFilename == "") and (options.inFilename == ""))):
    if (options.sampleSize < 0):
        print "please enter a positive number as the amount of vertices"
        exit(-1)
    if (options.sampleSize > 22000):
        print "not enough memory for such a large network"
        exit(-1)
    if (options.sampleSize < 10):
        print "minimum number of acteurs is 10"
        exit(-1) 
    print '...creating array...'
    myMirrAdj, clqs = createSampleEDG(options.sampleSize)
    print '...created...'
    if (options.outFilename <> ""):
        print '...writing to file...'
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        writeFile(clqs, filename + '.cliques')
        print 'written to file: ', filename

# Ein DIMACS-Graph soll untersucht werden
if ((options.sampleSize == 0) and ((options.dimacsFilename <> "") and (options.inFilename == ""))):
    filename = options.dimacsFilename
    print 'reading array from', filename, '...'
    myAdj = read_DIMACS_graph(filename)
    myMirrAdj = mirror(myAdj)
    if (not sizeOk(myMirrAdj)):
        print "size of network must be between 10 and 22000"
        exit(-1)   
    if (options.outFilename <> ""):
        print '...writing to file...'
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        print 'written to file: ', filename

# Ein CSV-File soll untersucht werden
if ((options.sampleSize == 0) and ((options.dimacsFilename == "") and (options.inFilename <> ""))):
    filename = options.inFilename
    print 'reading array from', filename, '...'
    myMirrAdj = readFile(filename)
    if (not sizeOk(myMirrAdj)):
        print "size of network must be between 10 and 22000"
        exit(-1)  
    if (options.outFilename <> ""):
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        print 'written to file: ', filename

logging.basicConfig(filename='MNTS_EDG.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.info('***  START ***')

for multEDG in range(1):

    print '...calculating density (can take some minutes)...'
    time7 = time.clock()
    print 'Density: ', calcDensity(myMirrAdj)
    time8 = time.clock()
    tt = str(time8 - time7)
    print 'time to calculate density: ', tt
    print '...start finding cliques...'
    time5 = time.clock()
    myDIMACSClique = MultiTabuSearch(myMirrAdj, iter, depth, options.nrOfCliques)
    time6 = time.clock()
    tt = str(time6 - time5)
    print 'time to find cliques: ', tt
    logging.info('time to find cliques: %s', tt)
    myDIMACSClique.reverse()
    print '*** Clique - Weight - Iteration - Time - Size ***'
    print 'The', myDIMACSClique.__len__(), 'best Cliques: '
    for clique in range(myDIMACSClique.__len__()):
        print clique + 1, ': ', myDIMACSClique[clique], myDIMACSClique[clique][0].__len__()

print 'the end'
logging.info('***  END ***')
