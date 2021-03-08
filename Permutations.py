import math
import numpy as np
import itertools
import sys

from ConnectedGraphs import connectedGraphs

def split(word):
    return [int(char) for char in word]

def difference(fromState, toState):
    difference = []
    for i in range(len(fromState)):
        difference.append(toState[i] - fromState[i])
    return difference

def generateNextStates(fromState, maxOutbreaks):
    nextStates = set(())
    if fromState == ["E", "E"]:
        nextStates.add(tuple(fromState))
        return nextStates
    for i in range(len(fromState) - 1):
        nextState = fromState.copy()
        if fromState[i] < 3:
            nextState[i] += 1
            nextStates.add(tuple(nextState))
        elif fromState[i] == 3:
            states = outbreak(fromState, i, maxOutbreaks)
            nextStates = nextStates.union(states)
    return nextStates

def outbreak(fromState, initialOutbreak, maxOutbreaks):
    cityStates = fromState[:-1]
    hotSpots = indices(cityStates, 3)
    twoCubes = indices(cityStates, 2)
    oneCubes = indices(cityStates, 1)
    numOutbreaks = len(hotSpots)
    if numOutbreaks > 1:
        numOutbreaks += len(twoCubes)
        if numOutbreaks > 2:
            numOutbreaks += len(oneCubes)
            if numOutbreaks > 3:
                numOutbreaks = len(fromState)
    states = addStates(numOutbreaks + 1, fromState, maxOutbreaks)
    return states

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

def addStates(totalOutbreaks, fromState, maxOutbreaks):
    numCities = len(fromState) - 1
    tuples = itertools.product(range(totalOutbreaks), repeat = numCities)
    states = set(())
    for thisTuple in tuples:
        numOutbreaks = 1
        listChange = list(thisTuple)
        state = fromState.copy()
        for i in range(len(state) - 1):
            numOutbreaks = max(numOutbreaks, listChange[i])
            state[i] = state[i] + listChange[i]
            if state[i] > 3:
                state[i] = 3
        state[len(state) - 1] += numOutbreaks
        if state[len(state) - 1] >= maxOutbreaks:
            state = ["E", "E"]
        states.add(tuple(state))
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

def probabilityTerm(edgeCount, totalEdges, p):
    return (p ** edgeCount) * ((1 - p) ** (totalEdges - edgeCount))

def requiredEdge(newCubes, newOuts):
    return newCubes + newOuts - 1

def requiredNonEdge(newCubes, newOuts, numCities):
    return newOuts * (numCities - newOuts) - newCubes

def probability(fromState, toState, p, cityProbability, totalEdges):
    newOuts = toState[len(fromState) - 1] - fromState[len(fromState) - 1]

    hs = indices(fromState[:-1], 3)
    hsCount = len(hs)
    nonHS = len(fromState) - hsCount - 1

    if newOuts == 0:
        return 1 / (len(fromState) - 1)
    newCubes = 0
    for i in range(len(fromState) - 1):
        newCubes += toState[i] - fromState[i]

    newHS = diff(indices(toState[:-1], 3), hs)

    requiredEdges = requiredEdge(newCubes, newOuts)
    requiredNonEdges = requiredNonEdge(newCubes, newOuts, len(fromState) - 1)

    probability = 0
    TEST = False
    if newOuts > 2 and len(newHS) > 0:
        return hsCount * cityProbability * badCase(hsCount, nonHS, hs, newHS, totalEdges, requiredEdges, requiredNonEdges, newCubes, p)
    else:
        if fromState == [3,0,1,0] and toState == (3,1,2,1):
            TEST = True
        return hsCount * cityProbability * goodCase(hsCount, nonHS, totalEdges, requiredEdges, requiredNonEdges, p, TEST)

def goodCase(countHS, nonOutbreak, totalEdges, requiredEdges, requiredNonEdges, p, TEST):
    sum = 0
    maxEdges = totalEdges - requiredNonEdges
    for i in range(requiredEdges, maxEdges + 1):
        term = probabilityTerm(i, totalEdges, p)
        coefficient = getGraphCounts(countHS, nonOutbreak, i, requiredEdges, TEST)
        sum += term * coefficient
    return sum

def badCase(countHS, nonOutbreak, hs, newHs, totalEdges, requiredEdges, requiredNonEdges, newCubes, fromState, toState, p):
    sum = goodCase(countHS, nonOutbreak, totalEdges, requiredEdges, requiredNonEdges, p, False)
    for i in range(0, len(newHs) + 1):
        for thisOne in itertools.combinations(newHs, i):
            newHsCubes = 0
            for i in thisOne:
                newHsCubes += (toState[i] - fromState[i])
                if newHsCubes <= newCubes:
                    sum += goodCase(countHS, nonOutbreak, totalEdges, requiredEdges, requiredNonEdge(newCubes - newHsCubes, newOuts, len(fromState) - 1), p, False)
    return sum


def getGraphCounts(countHS, nonOutbreak, edges, minEdges, TEST):
    optionalEdges = math.comb(nonOutbreak, 2)
    sum = 0
    connectedGraphs = numConnectedGraphsOnHS(countHS, edges, TEST)
    sum += (math.comb(optionalEdges, edges - minEdges) * connectedGraphs)
    return sum


def numConnectedGraphsOnHS(countHS, edges, TEST):
    if countHS == 1:
        return 1
    if edges == countHS - 1:
        return countHS ** (countHS - 2)
    if edges > math.comb(countHS - 1, 2):
        return math.comb(math.comb(countHS, 2), edges)
    index = edges - countHS
    return connectedGraphs[index][countHS]

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
                matrix[index][states[tuple(j)]] = probability(list(i), j, p, cityProbability, totalEdges)
    statesToFile(states)
    np.savetxt("Transitions.csv", matrix, delimiter=',', fmt='%1.5f')

if __name__ == "__main__":
    try:
        createMatrix(sys.argv[1], sys.argv[2], sys.argv[3])
    except:
        pring("There was an error.")
