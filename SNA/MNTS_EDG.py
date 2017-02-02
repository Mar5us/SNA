'''
@author: Marcus Kesper

Version 0.53 25.11.2012

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
        if len(filename)>3 and filename[-3:] == ".gz":  # file compressed with gzip
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
            i,j = int(i)-1, int(j)-1 # -1 for having nodes index starting on 0
            myArr[i][j] = 1
        elif line[0] == 'c':
            continue
        elif line[0] == 'p':
            p, name, n, nedges = line.split()
            # assert name == 'clq'
            n, nedges = int(n), int(nedges)
            myArr = np.int_([[0] * n for i in range(n)])
    f.close()
    return myArr

# Funktion: Fuellt ein Array mit Nullen
# Rueckgabewert: Das mit Nullen gefuellte Array
def initialize(size):
    myArr = np.int_([[0] * size for i in range(size)])
    return myArr

# Funktion: Fuellt ein Array einer bestimmten Dichte mit Zufallswerten
# Rueckgabewert: Das gefuellte Array
def fillRandom(myArr, density):
    nrOfActors = myArr.shape[0]
    for i in range(0, nrOfActors):
        for j in range(0, nrOfActors):
            if (i <> j):
                randVal1 = random.randint(0, 1000)
                randVal2 = random.randint(1, 100)
                if (randVal1 <= (1000 * density)): 
                    myArr[i][j] = randVal2
                else:
                    myArr[i][j] = 0
            else:
                myArr[i][j] = 0
    return myArr

# Funktion: Fuellt ein Array einer bestimmten Dichte mit Zufallswerten
# Rueckgabewert: Das gefuellte Array
def fillRandomAdv(myArr, density):
    nrOfActors = myArr.shape[0]
    nrofEdgesPerVertex = float((nrOfActors-1)*density)
    randVal1 = random.randint(80, 100)
    iMax = int(nrOfActors/100*randVal1)
    i = 0
    for acteur in randrange(0, nrOfActors-1):
        i = i + 1
        if (i > iMax):
            break  
        nrofEdgesPerVertexRandom = random.randint(int(nrofEdgesPerVertex-nrofEdgesPerVertex/5), int(nrofEdgesPerVertex+nrofEdgesPerVertex/5))
        for contacts in range(int(nrofEdgesPerVertexRandom/2)):
            randVal2 = random.randint(0, 100)
            randVal3 = random.randint(0, 100)
            randAkt = random.randint(0, nrOfActors-1)
            myArr[acteur][randAkt] = randVal2
            myArr[randAkt][acteur] = randVal3
    return myArr
        

# Funktion: Gibt ein Array auf die Konsole aus
def showArray(myArr):
    nrOfActors = myArr.shape[0]
    for i in range(nrOfActors):
        print i,': ',
        for j in range(nrOfActors):
            print myArr[i][j],
        print ''

# Funktion: Testet, ob die Netzwerkgroesse im richtigen Bereich liegt
# Rueckgabewert: True oder False
def sizeOk(myArr):
    return ((myArr.shape[0] >= 10) and (myArr.shape[0] <= 20000))

# Funktion: Liest ein Array von einem CSV-File
# Rueckgabewert: Das eingelesene Array mit dem Filenamen filename
def readFile(filename):
    newArr = np.genfromtxt(filename, delimiter=';', dtype=int)
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

# Funktion: Kreiert einen gerichteten und kantengewichteten Graphen mit 4 bis 8 Cliquen 
# unterschiedlicher Laenge
# Rueckgabewert: Ein Graph als zweidimensionales Array der Groesse size
def createSampleEDG(size):
    nrOfCliques = int(size * 0.001 + 5)
    edg = initialize(size)
    if (size <= 100):
        density = 0.05
    if ((size > 100) and (size <= 10000)):
        density = 0.01
    if ((size >10000) and (size <= 20000)):
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
            clqlength = random.randint(4, size/400+10) 
        while (clq.__len__() < clqlength):
            member = random.randint(0, size-1)
            if (not clq.__contains__(member)):
                clq.append(member)
        for acteurX in range(clq.__len__()):
            for acteurY in range(clq.__len__()):
                if ((acteurX == acteurY) or (randEDG[clq[acteurX]][clq[acteurY]] > 19)):
                    continue
                else:
                    randEDG[clq[acteurX]][clq[acteurY]] = random.randint(20,90)
        clq.sort(cmp=None, key=None, reverse=False)
        clqs.append((clq, weightOfClique(randEDG, clq)))
    clqs.sort(cmp=None, key=lambda x: x[1], reverse=True)
    print 'created cliques: '
    for clique in range(clqs.__len__()):
        print clique+1, ': ', clqs[clique], clqs[clique][0].__len__()
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
    #print 'Centrality: ', actSortByCent
    print 'Number of acteurs with centrality > 0: ', actSortByCent.__len__()
    return actSortByCent

# Funktion: berechnet die Dichte eines Graphen
# Rueckgabewert: Die Dichte des Graphen myArr
def calcDensity(myArr):
    nrOfActors = myArr.shape[0]
    nrOfEdges = 0
    for i in range(nrOfActors):
        for j in range(nrOfActors):
            if (myArr[i][j] > 0):
                nrOfEdges = nrOfEdges + 1
    density = round(float(nrOfEdges)/(nrOfActors*(nrOfActors-1)), 4)
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
    mult = (float(iterations)/float(iterMax))**2 #ergibt eine nichtlineare Kurve
    #Der Range der moeglichen Kandidaten fuer die Startclique vergroessert sich mit der Zeit
    actToCheck = int((float(nrOfCActors))/100*(mult*99+1))+1
    #logging.info('INITIAL CLIQUE actToCheck: %s %s', actToCheck, iterations)
    startActeur = random.randint(0, actToCheck-1)
    a, b = myActSortByCent[startActeur]
    #logging.info('INITIAL CLIQUE startActeur: %s', a)
    #logging.info('INITIAL CLIQUE value: %s', b)
    #Der erste Akteur der Startclique soll einer mit einem moeglichst hohen Centrality-Wert sein
    randClique.append(a)
    
    for acteur in randrange(0, nrOfActors-1):
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
    #logging.info('INITIAL CLIQUE randClique: %s', randClique)     
    return randClique

# Funktion: Berechnet die beiden Nachbarschaften ADD und SWAP und gibt die am 
# hoechsten bewerteten Cliquen sowie die neue Tabu-Liste zurueck
# Rueckgabewerte: 
#     bestCliqueAddCand, bestCliqueSwapCand: Jeweils der an besten geeignete Kandidat der beiden
#         Nachbarschaften
#     tabuADDCand, tabuSWAPCand, tabuSWAPADDCand: Die Kandidaten fuer die neue Tabu-Liste
#     swapCandidates.__len__(): Die Anzahl der SWAP-Kandidaten. Wichtig, weil die Laenge der
#         Tabu-Liste dynamisch ist
def neighborhoodAddSwap(myArr, myClique, myActSortByCent, tabuDROPList, tabuSWAPList, iterations, iterMax):
    bestCliqueAddCand = myClique[:]
    bestCliqueSwapCand = myClique[:]
    nrOfActorsPos = myActSortByCent.__len__()
    #logging.info('ADD SWAO nrOfActorsPos: %s', nrOfActorsPos)
    cliqueSize = myClique.__len__()
    tabuADDCand = -1
    tabuSWAPCand = -1
    tabuSWAPADDCand = -1
    swapCandDict = {}
    addCandidates = []
    swapCandidates = []
    mult = ((float(iterations)/float(iterMax))**3)+0.4 #ergibt eine nichtlineare Kurve
    if (mult > 1):
        mult = 1
    actToCheck = int((float(nrOfActorsPos))/100*(mult*99+1))
    #logging.info('ADD SWAP actToCheck: %s %s',actToCheck, iterations)
    for acteurPos in range(0, actToCheck):
        acteur, deg = myActSortByCent[acteurPos]
        #logging.info('ADD SWAP acteur: %s', acteur)
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

# berechnet die Nachbarschaft DROP: Sucht denjenigen Kandidaten, welcher mit dem geringsten Verlust entfernt werden kann
def neighborhoodDrop(myArr, myClique, tabuADDList):
    tabuCand = -1
    candDrop = -1
    bestCliqueDropCand = myClique[:]
    if (myClique.__len__() > 2):
        minNegSum = weightOfClique(myArr, bestCliqueDropCand)
        for testCand in randrange(0, bestCliqueDropCand.__len__()-1):
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

# die Funktion fuer die Berechnung einer Clique; setzt sich zusammen aus der Laenge und der Summe der Kantengewichte 
# zwischen den Mitgliedern der Clique 
# die Gegenseitigkeit ist noch nicht explizit beruecksichtigt (14.10.2012)
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

# prueft, ob eine Clique als Sub-Clique einer Liste von Cliquen vorkommt
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

# der eigentliche MN/TS for EDG Algorithmus
def MultiTabuSearch(myArr, iterMax, searchDepth, nrOfCliques):
    tabuADDlength = 2
    tabuDROPlength = 7
    iterations = 0
    steps = int(iterMax/10)
    maxClique = np.int_([])
    bestCliques = []
    print '...sorting acteurs by centrality (can take some minutes)...'
    time12 = time.clock()
    myActSortByCent = calcCentrality(myArr)
    time13 = time.clock()
    tt = time13-time12
    print 'time to sort ', myActSortByCent.__len__(),' acteurs by centrality: ', tt
    #logging.info('MSTN myActSortByCent: %s', myActSortByCent)
    startTime = time.clock()
    print '...start iterations...'
    while (iterations < iterMax):
        #logging.info('++++ iterations: ++++ %s', iterations)
        #timeX = time.clock()
        #time1 = time.clock()
        currentClique = initialClique(myArr, myActSortByCent, iterations, iterMax)
        #time2 = time.clock()
        #logging.info('MSTN time for initialClique: %s', time2-time1)
        #logging.info('MSTN initial clique: %s', currentClique)
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
            #logging.info('MSTN current clique: %s', currentClique)
            #logging.info('notImproved: %s', notImproved)
            #logging.info('iterations: %s', iterations)
            bestNeighborClique = []
            #logging.info('MAIN currentClique: %s', currentClique)  
            # berechnet die Nachbarschaften ADD und SWAP
            #time1 = time.clock()
            bestAddCliqueCand, bestSwapCliqueCand, tabuADDCand, tabuSWAPCand, tabuSWAPADDCand, nrOfSWAPCand = neighborhoodAddSwap(myArr, currentClique, myActSortByCent, tabuDROPList, tabuSWAPList, iterations, iterMax)
            #logging.info('MSTN bestAddCliqueCand: %s', bestAddCliqueCand)
            #logging.info('MSTN bestSwapCliqueCand: %s', bestSwapCliqueCand)
            #logging.info('MSTN tabuADDCand: %s', tabuADDCand)
            #logging.info('MSTN tabuSWAPCand: %s', tabuSWAPCand)
            #logging.info('MSTN tabuSWAPADDCand: %s', tabuSWAPADDCand)
            #logging.info('MSTN nrOfSWAPCand: %s', nrOfSWAPCand)
            #time2 = time.clock()
            #logging.info('MSTN time for bestAddCliqueCand/bestSwapCliqueCand: %s', time2-time1)
            # Nachbarschaft ADD auswaehlen, wenn vorhanden und groesser als SWAP Nachbarschaft
            if ((bestAddCliqueCand.__len__() > 0) and (weightOfClique(myArr, bestAddCliqueCand) > weightOfClique(myArr, bestSwapCliqueCand))): 
                # Nachbarschaft ADD auswaehlen
                bestNeighborClique = bestAddCliqueCand[:]
                #logging.info('*** SELECT ADD ***')
                # Tabu ADD Liste nachfuehren
                if (tabuADDList.__len__() >= tabuADDlength):
                    tabuADDList.pop(0) #mit append und pop(0) wird eine FIFO Liste implementiert
                tabuADDList.append(tabuADDCand)
                #logging.info('tabuADDList: %s', tabuADDList)
            else:
                # berechnet die Nachbarschaft DROP und vergleicht sie mit der SWAP Nachbarschaft
                #time1 = time.clock()
                bestDropCliqueCand, tabuDropCand = neighborhoodDrop(myArr, currentClique, tabuADDList)
                #logging.info('MSTN bestDropCliqueCand: %s', bestDropCliqueCand)
                #logging.info('MSTN tabuDropCand: %s', tabuDropCand)
                #time2 = time.clock()
                #logging.info('MSTN time for bestDropCliqueCand: %s', time2-time1)
                if (weightOfClique(myArr, bestDropCliqueCand) > weightOfClique(myArr, bestSwapCliqueCand)):
                    # Nachbarschaft DROP auswaehlen
                    bestNeighborClique = bestDropCliqueCand[:]
                    #logging.info('*** SELECT DROP ***')
                    # Tabu DROP Liste nachfuehren
                    if (tabuDROPList.__len__() >= tabuDROPlength):
                        tabuDROPList.pop(0) #mit append und pop(0) wird eine FIFO Liste implementiert
                    tabuDROPList.append(tabuDropCand)
                    #logging.info('tabuDROPList: %s', tabuDROPList)
                else:
                    if (bestSwapCliqueCand.__len__() > 0):
                        # Nachbarschaft SWAP auswaehlen
                        bestNeighborClique = bestSwapCliqueCand[:]
                        #logging.info('*** SELECT SWAP ***')
                        # Tabu SWAP Liste nachfuehren
                        #logging.info('MAIN nrOfSWAPCand: %s', nrOfSWAPCand)  
                        tabuSWAPListlength = random.randint(1, nrOfSWAPCand) + 7
                        #logging.info('MAIN tabuSWAPListlength: %s', tabuSWAPListlength)
                        while (tabuSWAPList.__len__() > tabuSWAPListlength):
                            tabuSWAPList.pop(0) #mit append und pop(0) wird eine FIFO Liste implementiert
                        # Tabu ADD Liste nachfuehren
                        if (tabuADDList.__len__() >= tabuADDlength):
                            tabuADDList.pop(0) #mit append und pop(0) wird eine FIFO Liste implementiert
                        tabuADDList.append(tabuSWAPADDCand)
                        #logging.info('tabuADDList: %s', tabuADDList)
                        tabuSWAPList.append(tabuSWAPCand)
                        #logging.info('tabuSWAPList: %s', tabuSWAPList)
            
            if (bestNeighborClique.__len__() > 0):
                currentClique = bestNeighborClique[:]
                currentClique.sort(cmp=None, key=None, reverse=False)
            notImproved = notImproved + 1
            iterations = iterations + 1
            if ((iterations % steps) == 0):
                completed = round(float(iterations)/iterMax*100, 0)
                if (completed > 100):
                    completed = 100
                print completed, '% completed'
            if (weightOfClique(myArr, currentClique) >  weightOfClique(myArr, localBestClique)):
                notImproved = 0
                localBestClique = currentClique[:]
            #logging.info('MSTN localBestClique within notimproved: %s', localBestClique)
        if (searchDepth == 0):
            iterations = iterations + 1
            if ((iterations % steps) == 0):
                completed = round(float(iterations)/iterMax*100, 0)
                if (completed > 100):
                    completed = 100
                print completed, '% completed'
        actTime = time.clock()
        passedTime = actTime - startTime
        #logging.info('MSTN localBestClique: %s', localBestClique)
        if (localBestClique.__len__() > 2):
            bestClqCand = ((localBestClique, weightOfClique(myArr, localBestClique), iterations, passedTime))
            if ((not bestCliques.__contains__(bestClqCand)) and ((bestCliques.__len__() < (nrOfCliques+1)) or (weightOfClique(myArr, localBestClique) >= weightOfClique(myArr, bestCliques[0])))):
                if (not subClq(bestClqCand, bestCliques)):
                    bestCliques.append(bestClqCand)
                    #logging.info('MSTN added to list: %s', bestClqCand)
                    bestCliques.sort(cmp=None, key=lambda x: x[1], reverse=False)
                    #logging.info('MSTN bestCliques: %s', bestCliques)
                    # prueft ob bereits gefundene Cliquen Subcliquen der neuen Clique sind.
                    #logging.info('MSTN bestCliques.__len__(): %s', bestCliques.__len__())
                    bestCliquesTemp = bestCliques[:]
                    if (bestCliques.__len__() > 1):
                        for clqs in range(0, bestCliques.__len__()-1):
                            #logging.info('MSTN clqs: %s', clqs)
                            clq = bestCliques[clqs]
                            if (subClq(clq, bestCliques)):
                                bestCliquesTemp.remove(clq)
                    #print 'maxClique: ',localBestClique, 'weight: ', weightOfClique(myArr, localBestClique), 'it: ', iterations, 'time: ', passedTime
                    #logging.info('MSTN maxClique: %s', localBestClique)
                    bestCliques = bestCliquesTemp[:]
                    if (bestCliques.__len__() > nrOfCliques):
                        bestCliques.pop(0)
        if (weightOfClique(myArr, localBestClique) > weightOfClique(myArr, maxClique)):                
            maxClique = localBestClique[:]
        #timeY = time.clock()
        #logging.info('MSTN time per iteration: %s', timeY-timeX)
    return bestCliques


parser = optparse.OptionParser()
parser.add_option("-f", "--dimacs", dest="dimacsFilename", default="", help="DIMACS file to load", metavar="FILE")
parser.add_option("-s", "--sample", dest="sampleSize", type="int", default=0, help="creates a sample network of size SAMPLESIZE with cliques - minimum size = 10; maximum size = 20000")
parser.add_option("-i", "--iterations", dest="iter", type="int", default=0, help="defines the number of iterations")
parser.add_option("-d", "--depth", dest="depth", type="int", default=-1, help="defines the search depth (0 means no local search)")
parser.add_option("-o", "--out", dest="outFilename", default="", help="name of the output file (adjacency matrix) in csv format")
parser.add_option("-c", "--in", dest="inFilename", default="", help="name of the input file (adjacency matrix) in csv format")
parser.add_option("-n", "--cliques", dest="nrOfCliques", type="int", default=10, help="number of cliques to find - default is 10")
(options, args) = parser.parse_args()


print 'options: ', options
print 'args: ', args

if (options.nrOfCliques < 1):
    print "the number of cliques to find must be > 0"
    exit(-1)
    
if (options.iter == 0):
    print "please specify number of iterations"
    exit(-1)
else:
    iter = options.iter
    
if (options.depth < 0):
    print "please specify the search depth"
    exit(-1)
else:
    depth = options.depth

if ((options.sampleSize <> 0) and ((options.dimacsFilename <> "") or (options.inFilename <> ""))):
    print "you can't specify a filename AND create a sample network"
    exit(-1)

if ((options.dimacsFilename <> "") and (options.inFilename <> "")):
    print "you can't specify a dimacs filename AND a csv filename"
    exit(-1)

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
        writeFile(clqs, filename+'.cliques')
        print 'written to file: ', filename
    #showArray(myMirrAdj)

if ((options.sampleSize == 0) and ((options.dimacsFilename <> "") and (options.inFilename == ""))):
    filename = options.dimacsFilename
    myAdj = read_DIMACS_graph(filename)
    myMirrAdj = mirror(myAdj)
    if (not sizeOk(myMirrAdj)):
        print "size of network must be between 10 and 20000"
        exit(-1)   
    if (options.outFilename <> ""):
        print '...writing to file...'
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        print 'written to file: ', filename

if ((options.sampleSize == 0) and ((options.dimacsFilename == "") and (options.inFilename <> ""))):
    filename = options.inFilename
    myMirrAdj = readFile(filename)
    if (not sizeOk(myMirrAdj)):
        print "size of network must be between 10 and 20000"
        exit(-1)  
    if (options.outFilename <> ""):
        filename = options.outFilename
        writeFile(myMirrAdj, filename)
        print 'written to file: ', filename

logging.basicConfig(filename='myPythonLog', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.info('***  START ***')


'''
iter = 6700
depth = 20
filename = 'c-fat500-5.clq'


#DIMACS Tests 
myAdj = read_DIMACS_graph(filename)
myMirrAdj = mirror(myAdj)
#writeFile(myAdj, 'brock200_1.csv')
print 'Read DIMACS Test File - Nodes', myMirrAdj.shape[0]
#print 'Read DIMACS Test File - Adj', showArray(myMirrAdj)
#writeFile(myMirrAdj, "brock800_1.csv")
'''
'''
#Tests mit selbst generiertem Array

print '...creating array...'
time1 = time.clock()
myMirrAdj = createSampleEDG(1000)
time2 = time.clock()
tt = str(time2-time1)
#print 'time for creating the array: ', tt
logging.info('MAIN time to create: %s', tt)
print '...created...'
#writeFile(myMirrAdj, 'mySampleEDG.csv')

iter = 2000
depth = 20
#showArray(myMirrAdj)
'''

    #print '....writing array to file...'
    #time3 = time.clock()
    #writeFile(myEDGArray, 'EDGArray1000.csv')
    #print '....file written...'
    #print '....loading file...'
    #myEDGArray = readFile('EDGArray10000.csv')
    #time4 = time.clock()
    #tt = str(time4-time3)
    #print 'Zeit fuer das Speichern des Arrays: ', tt
    #logging.info('MAIN time to save: %s', tt)
    #print '...file saved...'


for multEDG in range(1):

    print '...calculating density (can take some minutes)...'
    time7 = time.clock()
    #print 'Density: ', calcDensity(myMirrAdj)
    time8 = time.clock()
    tt = str(time8-time7)
    print 'time to calculate density: ', tt
    print '...start finding cliques...'
    time5 = time.clock()
    # Der erste Wert ist die max. Anzahl Iterationen;
    # der zweite Wert ist die Suchtiefe
    myDIMACSClique = MultiTabuSearch(myMirrAdj, iter, depth, options.nrOfCliques)
    time6 = time.clock()
    tt = str(time6-time5)
    print 'time to find cliques: ', tt
    logging.info('MAIN time to calculate: %s', tt)
    #logging.info('MAIN Groesse der Clique: %s', myDIMACSClique.__len__())
    myDIMACSClique.reverse()
    print '*** Clique - Weight - Iteration - Time - Size ***'
    print 'The', myDIMACSClique.__len__(),'best Cliques: '
    for clique in range(myDIMACSClique.__len__()):
        print clique+1, ': ', myDIMACSClique[clique], myDIMACSClique[clique][0].__len__()
        #logging.info('MAIN myDIMACSClique: %s', myDIMACSClique)

    print 'the end'
    logging.info('***  END ***')
