import genetic
import math
import queue
import random

# Test fitness function
def fitnessFun(x):
    return 1/((x / 100 - 15) ** 6 + 0.2) - math.sin(x / 100) + 1


def findAllPathsUtil(nodes, links, visited, node, goal, path, paths):
    visited[node] = True
    path.append(node)

    if goal == node:
        paths.append(path[:])
    else:
        for child in expand(node, links):
            if visited[child] == False:
                findAllPathsUtil(nodes, links, visited, child, goal, path, paths)

    path.pop()
    visited[node] = False

def findAllPaths(nodes, links, startNode, goalNode):
    visited = []
    for n in nodes:
        visited.append(False)

    paths = []
    path = []

    findAllPathsUtil(nodes, links, visited, startNode, goalNode, path, paths)

    return paths

def expand(node, links):
    children = []
    for l in links:
        if l[0] == node:
            children.append(l[1])
        else:
            if l[1] == node:
                children.append(l[0])
    return children

def getBitsNum(numPaths, numStreams):
    powerTwo = 1
    num = 2
    while numPaths > num:
        powerTwo += 1
        num *= 2
    return powerTwo * numStreams

def bonusCoeffFun(load):
    if load <= 0.25:
        return 40
    else:
        if load <= 0.75:
            return 15
        else:
            return 5

def decodeGenotype(person):
    global numberStreams
    personBinaryLenght = person.bit_length()

    extractConstant = 1
    extractNumber = 0
    fenotype = []
    for i in range(0, numberStreams):
        for j in range(0, numberBitsInGenotype // numberStreams):
            if (i * numberBitsInGenotype // numberStreams + j) < personBinaryLenght:
                extractNumber = extractNumber | ((person & extractConstant) >> i * numberBitsInGenotype // numberStreams)
                extractConstant = extractConstant << 1
        fenotype.append(extractNumber)
        extractNumber = 0
    fenotype.reverse()

    return fenotype


# Custom controller fitness function
def SDNFitnessFun(person):
    global links
    global linksCapacities
    global streams

    # Decode genotype
    fenotype = decodeGenotype(person)

    # Select relevant paths
    paths = []
    for i in range(0, len(fenotype)):
        paths.append(streamsPaths[i][fenotype[i]])

    linksLoad = []
    for i in range(0, len(links)):
        linksLoad.append(0)

    for i in range(0, len(links)):
        sum = 0
        for j in range(0, len(paths)):
            for k in range(0, len(paths[j]) - 1):
                if paths[j][k] == links[i][0] and paths[j][k + 1] == links[i][1] or paths[j][k] == links[i][1] and paths[j][k + 1] == links[i][0]:
                    sum += streams[j][2]
        linksLoad[i] = sum / linksCapacities[i]

    sum = 0
    for i in range(0, len(linksLoad)):
        sum += bonusCoeffFun(linksLoad[i])
    return float(sum)



nodes = [0, 1, 2, 3, 4]
links = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (0, 3), (0, 4)]
linksCapacities = [60, 45, 40, 70, 65, 65, 50]
streams = [(0, 1, 10), (2, 0, 16), (2, 1, 25)] # Stream: (srcNode, trgNode, capacityRequired)

streamsPaths = []
for s in streams:
    baz = findAllPaths(nodes, links, s[0], s[1])[:]
    # print(baz)
    streamsPaths.append(baz)

numbersPaths = [];
for s in streamsPaths:
    numbersPaths.append(len(s))

numberStreams = len(streams)
numberBitsInGenotype = getBitsNum(max(numbersPaths), numberStreams)

answer = genetic.executeGeneticAlgoritm(SDNFitnessFun, numberBitsInGenotype, 100, 0.01, 0.75, True)
fenotype = decodeGenotype(answer)

paths = []
for i in range(0, len(fenotype)):
    paths.append(streamsPaths[i][fenotype[i]])

print("Best selection of paths:")
print(paths)