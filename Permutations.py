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

def generateNextStates(fromState):
    nextStates = set(())
    for i in range(len(fromState) - 1):
        nextState = fromState.copy()
        if fromState[i] < 3:
            nextState[i] += 1
            nextStates.add(tuple(nextState))
        elif fromState[i] == 3:
            states = outbreak(fromState, i)
            newStates.union(states)
    return nextStates

def outbreak(fromState, initialOutbreak):
    cityStates = fromState[:-1]
    hotSpots = indices(cityStates, 3)
    twoCubes = indices(cityStates, 2)
    oneCubes = indices(cityStates, 1)

    if numOutbreaks > 1:
        numOutbreaks += len(twoCubes)
        if numOutbreaks > 2:
            numOutbreaks += len(oneCubes)
            if numOutbreaks > 3:
                numOutbreaks = len(fromState)

    states = addStates(numOutbreaks, fromState)
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

def addStates(numOutbreaks, fromState):
    numCities = len(fromState) - 1
    tuples = itertools.product(range(numOutbreaks), repeat = numCities)
    states = set(())
    for thisTuple in tuples:
        numOutbreaks = 1
        listChange = list(thisTuple)
        state = fromState.copy()
        for i in range(len(state) - 1):
            newOutbreaks = max(numOutbreaks, listChange[i])
            state[i] = state[i] + listChange[i]
            if state[i] > 3:
                state[i] = 3
        state[len(state) - 1] += numOutbreaks
        states.add(tuple(state))
    return states

def allStates(numCities, maxOutbreaks):
    states = {}
    tuples = itertools.product(range(4), repeat = numCities)
    indexLoc = 0
    for outbreak in range(maxOutbreaks):
        for thisTuple in tuples:
            stateList = list(thisTuple)
            stateList.append(outbreak)
            states[tuple(stateList)] = indexLoc
            indexLoc += 1
    return states

def createMatrix(numCities, maxOutbreaks, p):
    states = allStates(numCities, maxOutbreaks)
    matrix = np.zeros((len(states), len(states)))
    for i in states:
        nextStates = generateNextStates(list(i))
        index = states[i]
        for j in nextStates:
            matrix[index][states[tuple(j)]] = 1
    np.savetxt("Fred.csv", matrix, delimiter=',')

createMatrix(5, 3, 0.6)
