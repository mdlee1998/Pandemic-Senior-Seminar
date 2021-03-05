import math
import numpy as np
import itertools

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


def createMatrix(numCities, maxOutbreaks, p):
    totalEdges = math.comb(numCities, 2)
    states = allStates(numCities, maxOutbreaks)
    matrix = np.zeros((len(states), len(states)))
    cityProbability = 1 / numCities

    for i in states:
        nextStates = generateNextStates(list(i), maxOutbreaks)
        index = states[i]
        for j in nextStates:
            matrix[index][states[tuple(j)]] = 1
    statesToFile(states)
    np.savetxt("Transitions.csv", matrix, delimiter=',', fmt='%1.5f')

createMatrix(3, 2, 0.6)
