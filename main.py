import genetic
import math
import queue
import random
import datetime
from datetime import timedelta

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
    global streamsPaths
    personBinaryLenght = person.bit_length()

    '''
        Decompose binary string into an array of numbers, that represents a list of
        path variant indexes.
    '''
    extractConstant = 1
    extractNumber = 0
    phenotype = []
    for i in range(0, numberStreams):
        for j in range(0, numberBitsInGenotype // numberStreams):
            if (i * numberBitsInGenotype // numberStreams + j) < personBinaryLenght:
                extractNumber = extractNumber | ((person & extractConstant) >> i * numberBitsInGenotype // numberStreams)
                extractConstant = extractConstant << 1
        phenotype.append(extractNumber)
        extractNumber = 0
    phenotype.reverse()

    '''
        If the genetic algorithm generate a number, that greater than numbers of paths variants,
        then we just floor that number to the maximum index of array, that consist these variants.
    '''
    for i in range(0, len(phenotype)):
        if phenotype[i] >= len(streamsPaths[i]):
            phenotype[i] = len(streamsPaths[i]) - 1

    return phenotype


# Custom controller fitness function
def SDNFitnessFun(person):
    global links
    global linksCapacities
    global streams
    global streamsPaths

    # Decode genotype
    phenotype = decodeGenotype(person)

    # Select paths corresponding to phenotype
    paths = []
    for i in range(0, len(phenotype)):
        paths.append(streamsPaths[i][phenotype[i]])

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


'''
nodes = [0, 1, 2, 3, 4]
links = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (0, 3), (0, 4)]
linksCapacities = [60, 45, 40, 70, 65, 65, 50]
streams = [(0, 1, 10), (2, 0, 16), (2, 1, 25)] # Stream: (srcNode, trgNode, capacityRequired)
'''
random.seed()

nodesNumber = 10
linksNumber = 20
minLinkCapacity = 20
maxLinkCapacity = 100
streamsNumber = 3

# Generate nodes
nodes = []
for i in range(0, nodesNumber):
    nodes.append(i)

sumExecutionTimes = 0
print("--------------------------------------------------------------------")
for iteration in range(0, 100):
    # Generate links
    links = []
    for i in range(0, linksNumber):
        while True:
            nodeFirst = random.randint(0, nodesNumber - 1)
            nodeSecond = random.randint(0, nodesNumber - 1)
            while nodeFirst == nodeSecond:
                nodeSecond = random.randint(0, nodesNumber - 1)
            if not ((nodeFirst, nodeSecond) in links or (nodeSecond, nodeFirst) in links):
                break
        links.append(tuple([nodeFirst, nodeSecond]))

    # Generate link capacities
    linksCapacities = []
    for i in range(0, linksNumber):
        linksCapacities.append(random.randint(minLinkCapacity, maxLinkCapacity))

    # Generate streams
    streams = []
    for i in range(0, streamsNumber):
        nodeFirst = random.randint(0, nodesNumber - 1)
        nodeSecond = random.randint(0, nodesNumber - 1)
        while nodeFirst == nodeSecond:
            nodeSecond = random.randint(0, nodesNumber - 1)
        streamReqCapacity = random.randint(1, maxLinkCapacity // 2)
        streams.append(tuple([nodeFirst, nodeSecond, streamReqCapacity]))

    print("Input data:")
    print(nodes)
    print(links)
    print(linksCapacities)
    print(streams)

    # Fix time of algorithm start
    startTime = datetime.datetime.now()

    # Find paths for current streams
    streamsPaths = []
    for s in streams:
        baz = findAllPaths(nodes, links, s[0], s[1])[:]
        # print(baz)
        streamsPaths.append(baz)

    # Calculate array of path variants numbers for util purposes
    numbersPaths = [];
    for s in streamsPaths:
        numbersPaths.append(len(s))

    # Calculate number bits in genotype
    numberStreams = len(streams)
    numberBitsInGenotype = getBitsNum(max(numbersPaths), numberStreams)

    # Execution of genetic algorithm and receive answer from it
    answer = genetic.executeGeneticAlgoritm(SDNFitnessFun, numberBitsInGenotype, 100, 0.01, 0.75, True)
    phenotype = decodeGenotype(answer)

    # Fix time of algorithm stop and calculate execution time
    stopTime = datetime.datetime.now()
    executionTime = (stopTime - startTime).total_seconds()
    sumExecutionTimes += executionTime

    paths = []
    for i in range(0, len(phenotype)):
        paths.append(streamsPaths[i][phenotype[i]])

    print("\nBest selection of paths: {0}".format(paths))
    print("\nExecution time equal {0:.6} milliseconds".format(executionTime * 1000))
    print("--------------------------------------------------------------------")

print("\nSUMMARY:")
print("Average execution time equal {0:.6} milliseconds".format(sumExecutionTimes * 1000 / 100))
