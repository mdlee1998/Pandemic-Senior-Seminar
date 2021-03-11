import math
import numpy as np
import itertools
import sys

from ConnectedGraphs import connectedGraphs


def difference(fromState, toState):
    difference = []
    for i in range(len(fromState)):
        difference.append(toState[i] - fromState[i])
    return difference

def generateNextStates(fromState, maxOutbreaks):
    outbroke = False
    nextStates = set(())
    if fromState == ["E", "E"]:
        nextStates.add(tuple(fromState))
        return nextStates
    for i in range(len(fromState) - 1):
        nextState = fromState.copy()
        if fromState[i] < 3:
            nextState[i] += 1
            nextStates.add(tuple(nextState))
        elif fromState[i] == 3 and not outbroke:
            outbroke = True
            states = outbreak(fromState, maxOutbreaks)
            nextStates = nextStates.union(states)
    return nextStates


def indices(lst, element):
    result = []
    offset = -1
    while True:
        try:
            offset = lst.index(element, offset+1)
        except ValueError:
            return result
        result.append(offset)

def diff(li1, li2):
    return (list(list(set(li1)-set(li2))))

def addStates(hotSpots, state, endgameOutbreaks):
    states = set(())
    repeater = len(state) - len(indices(state[:-1], 3)) - 1
    if repeater < 1:
        if state[len(state) - 1] >= endgameOutbreaks - 1:
            states.add(("E", "E"))
        else:
            newState = state.copy()
            newState[len(newState) - 1] += 1
            states.add(tuple(newState))
        return states
    tuples = itertools.product(range(len(hotSpots) + 1), repeat = repeater)
    for thisTuple in tuples:
        newOutbreaks = []
        newState = state.copy()
        initialOutbreaks = newState[len(newState) - 1]
        minOutbreaks = 1
        counter = 0
        for i in range(len(newState) - 1):
            if newState[i] < 3:
                minOutbreaks = max(minOutbreaks, thisTuple[counter])
                newState[i] += thisTuple[counter]
                counter += 1
            if newState[i] > 3:
                newOutbreaks.append(i)
                newState[i] = 3
        for i in range(minOutbreaks, len(hotSpots) + 1):
            newState[len(newState) - 1] = i + initialOutbreaks
            if newState[len(newState) - 1] >= endgameOutbreaks:
                newState = ["E", "E"]
                newOutbreaks = []
            states.add(tuple(newState))
        if newOutbreaks:
            states = states.union(addStates(newOutbreaks, newState, endgameOutbreaks))
    return states



def outbreak(fromState, maxOutbreaks):
    hotSpots = indices(fromState[:-1], 3)
    states = addStates(hotSpots, fromState, maxOutbreaks)
    return states

def allStates(numCities, maxOutbreaks):
    states = {}
    tuples = itertools.product(range(4), repeat = numCities)
    size = 4 ** numCities
    indexLoc = 0
    for thisTuple in tuples:
        for outbreak in range(maxOutbreaks):
            stateList = list(thisTuple)
            stateList.append(outbreak)
            states[tuple(stateList)] = (outbreak * size) + indexLoc
        indexLoc += 1
    states[("E", "E")] = (4 ** numCities) * maxOutbreaks
    return states

def statesToFile(states):
    stateList = [None] * len(states)
    for i in states:
        stateList[states[i]] = str(i).replace(",","")
    f = open("States.csv", "w")
    for i in stateList:
        f.write(i)
        f.write("\n")

def probability(fromState, toState, p, cityProbability, totalEdges):
    newOuts = toState[len(fromState) - 1] - fromState[len(fromState) - 1]
    if newOuts == 0:
        return 1 / (len(fromState) - 1)

    hs = indices(fromState[:-1], 3)
    newHS = diff(indices(toState[:-1], 3), hs)

    probability = 0
    TEST = False
    if fromState == [0,3,2,3,0] and toState == (3,3,3,3,3):
        TEST = True
    if newOuts > 2 and len(newHS) > 0:
        return cityProbability * badCase(fromState, toState, newOuts, totalEdges, hs, p, TEST)
    else:
        return cityProbability * goodCase(fromState, toState, newOuts,totalEdges, hs, p)


def probabilityTerm(edgeCount, totalEdges, p):
    return (p ** edgeCount) * ((1 - p) ** (totalEdges - edgeCount))

def requiredEdge(newCubes, newOuts):
    return newCubes + newOuts - 1

def requiredNonEdge(newCubes, newOuts, numCities):
    return newOuts * (numCities - newOuts) - newCubes



#Gets the number of connected graphs based on a given number of outbreaking cities and a given number of edges
def numConnectedGraphsOnHS(countHS, edges):
    #If there is only one outbreaking city
    if countHS == 1:
        return 1
    #Number of edges is one less than number of outbreaking cities; basically, number of trees on outbreaking cities vertices
    if edges == countHS - 1:
        return countHS ** (countHS - 2)
    #If there are more edges than outbreaking cities - 1; all graphs with this many edges must be connected, so we only count
    #how many of these graphs there are
    if edges > math.comb(countHS - 1, 2):
        return math.comb(math.comb(countHS, 2), edges)
    #If no other situation is fulfilled, get the count
    index = edges - countHS
    return connectedGraphs[index][countHS]

#Gets the number of potential graphs that have no new cubes given a specific number of outbreaking cities, hotspots, and edges.
#Graphs with new cubes will have a multiple of this value
def getGraphsNoCubes(countHS, newOuts, nonHs, edges):
    #Optional edges between nonOutbreaking cities
    optionalEdges = math.comb(nonHs + (countHS - newOuts), 2)
    sum = 0
    #Iterates through the number of possible edges
    for i in range(newOuts - 1, edges + 1):
        connectedGraphs = numConnectedGraphsOnHS(newOuts, i)
        #Multiplies number of connected graphs by the number of possible hotspots to choose from.  Subtracts one from both
        #due to the drawn card being already determined, we are only choosing from the remaining hotspots
        connectedGraphs *= math.comb(countHS - 1, newOuts - 1)
        #Multiplies these connected graphs by the number of possible locations for an optional edge
        sum += (math.comb(optionalEdges, edges - i) * connectedGraphs)
        if newOuts < 2:
            break
    return sum

#Gets the total number of graphs based on a specific number of hotspots, how
#many outbreaks, non-hotspots, edges and difference between states
def getGraphCounts(countHS, newOuts, nonHs, edges, difference):
    totalCubes = 0
    mult = 1
    #Number of configurations of edges from outbreak to nonoutbreaking cities
    for i in difference:
        totalCubes += i
        mult *= math.comb(newOuts, i)
    sum = getGraphsNoCubes(countHS, newOuts, nonHs, edges - totalCubes)
    return sum * mult

def goodCase(fromState, toState, newOuts, totalEdges, hs, p):
    newCubes = 0
    for i in range(len(fromState) - 1):
        newCubes += toState[i] - fromState[i]

    requiredEdges = requiredEdge(newCubes, newOuts)
    requiredNonEdges = requiredNonEdge(newCubes, newOuts, len(fromState) - 1)
    maxEdges = totalEdges - requiredNonEdges
    countHS = max(len(hs), newOuts)

    difference = []
    for i in range(len(fromState) - 1):
        difference.append(toState[i] - fromState[i])

    sum = 0
    for i in range(requiredEdges, maxEdges + 1):
        term = probabilityTerm(i, totalEdges, p)
        coefficient = getGraphCounts(countHS, newOuts, len(fromState) - len(hs) - 1, i, difference)
        sum += term * coefficient
    return sum * countHS

def badCase(fromState, toState, newOuts, totalEdges, hs, p, TEST):
    newCubes = 0
    for i in range(len(fromState) - 1):
        newCubes += toState[i] - fromState[i]

    requiredEdges = requiredEdge(newCubes, newOuts)
    countHS = len(hs)

    newHotSpotCubes = {}

    difference = []

    for i in range(len(toState) - 1):
        difference.append(toState[i] - fromState[i])
        if toState[i] == 3:
            newHotSpotCubes[i] = toState[i] - fromState[i]
    possibleOutbreaks = []
    tried = set(())
    hotSpots = []
    for i in range(len(toState) - 1):
        if toState[i] == 3 and fromState[i] + countHS > 3:
            hotSpots.append(i)
    tuples = itertools.combinations(hotSpots, newOuts)
    sum = 0

    for thisTuple in tuples:

        oldHotSpot = list(set(thisTuple).intersection(hs))
        if len(oldHotSpot) in tried:
            continue
        tried.add(len(oldHotSpot))
        newHotSpot = []
        maxNeeded = 0
        for i in thisTuple:
            if i not in oldHotSpot:
                newHotSpot.append(i)
                maxNeeded = max(maxNeeded, difference[i])
        if len(oldHotSpot) > maxNeeded:
            cubes = newCubes
            for i in thisTuple:
                cubes -= newHotSpotCubes[i]
            if cubes >= 0:
                requiredNonEdges = requiredNonEdge(cubes, newOuts, len(toState) - 1)
                for i in range(requiredEdges, totalEdges - requiredNonEdges + 1):
                    term = probabilityTerm(i, totalEdges, p)
                    coefficient = badGetGraphCounts(oldHotSpot, newHotSpot, countHS, newOuts, len(fromState) - len(oldHotSpot) - len(newHotSpot) - 1, i, difference, TEST)
                    sum += term * coefficient
    return sum * countHS



#Gets the total number of graphs based on a specific number of hotspots, how
#many outbreaks, non-hotspots, edges and difference between states
def badGetGraphCounts(oldHotSpot, newHotSpots, totalOriginalHotspots, newOuts, nonHs, edges, difference, TEST):
    totalCubes = 0
    mult = 1

    newHotSpotCubes = []
    for i in newHotSpots:
        newHotSpotCubes.append(difference[i])
        difference[i] = 0
    #Number of configurations of edges from outbreak to nonoutbreaking cities
    newHs = []
    for i in range(len(difference)):
        if i not in newHotSpots:
            totalCubes += difference[i]
            mult *= math.comb(newOuts, difference[i])
        else:
            newHs.append(i)
    sum = badGetGraphsNoCubes(oldHotSpot, newHotSpotCubes, totalOriginalHotspots, newOuts, nonHs, edges - totalCubes, TEST)
    return sum * mult
#oldHotSpot: Indices of original hotspots that outbreak
#newHotSpot: Number of cubes necessary to reach new hotspot
#total number of original hotspots
#newOuts: Number of new outbreaks
#nonHs: Number of nonoutbreaking vertices
#edges: current number of edges
def badGetGraphsNoCubes(oldHotSpot, newHotSpot, totalHS, newOuts, nonHs, edges, TEST):
    newHotSpotsEdges = 0
    countHS = len(oldHotSpot)
    #Optional edges between nonOutbreaking cities
    optionalEdges = math.comb(nonHs + (countHS + len(newHotSpot) - newOuts), 2)
    sum = 0

    newHotSpotsEdgeGraph = 1
    for i in newHotSpot:
        newHotSpotsEdges += (i + 1)
        edges -= (i + 1)
        newHotSpotsEdgeGraph *= math.comb(countHS, i + 1)

    #Iterates through the number of possible edges
    for i in range(newOuts - len(newHotSpot) - 1, edges + 1):
        connectedGraphs = numConnectedGraphsOnHS(newOuts - len(newHotSpot), i) * newHotSpotsEdgeGraph
        #Multiplies number of connected graphs by the number of possible hotspots to choose from.  Subtracts one from both
        #due to the drawn card being already determined, we are only choosing from the remaining hotspots
        connectedGraphs *= math.comb(totalHS - 1, newOuts - len(newHotSpot) - 1)

        #Multiplies these connected graphs by the number of possible locations for an optional edge
        sum += (math.comb(optionalEdges, edges - i) * connectedGraphs)
        if newOuts < 2:
            break
    return sum

def createMatrix(numCities, maxOutbreaks, p):
    totalEdges = math.comb(numCities, 2)
    states = allStates(numCities, maxOutbreaks)
    matrix = np.zeros((len(states), len(states)))
    cityProbability = 1 / numCities

    for i in states:
        nextStates = generateNextStates(list(i), maxOutbreaks)
        index = states[i]
        for j in nextStates:
            if j != ('E', 'E'):
                matrix[index][states[j]] = probability(list(i), j, p, cityProbability, totalEdges)
    statesToFile(states)
    np.savetxt("Transitions.csv", matrix, delimiter=',', fmt='%1.5f')

if __name__ == "__main__":
    #try:
    numCities = int(sys.argv[1])
    maxOutbreaks = int(sys.argv[2])
    p = float(sys.argv[3])
    createMatrix(numCities, maxOutbreaks, p)
