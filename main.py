import genetic
import random
import datetime
from datetime import timedelta

def findAllPathsUtil(nodes, links, visited, node, goal, path, paths):
    '''Recursive function for finding all paths for stream'''
    visited[node] = True
    path.append(node)

    if goal == node:
        paths.append(path[:])
    else:
        for child in getChildren(node, links):
            if visited[child] == False:
                findAllPathsUtil(nodes, links, visited, child, goal, path, paths)

    path.pop()
    visited[node] = False

def findAllPaths(nodes, links, startNode, goalNode):
    '''Function, that starts recursive searching all paths for stream'''
    visited = []
    for n in nodes:
        visited.append(False)

    paths = []
    path = []

    findAllPathsUtil(nodes, links, visited, startNode, goalNode, path, paths)

    return paths

def getChildren(node, links):
    '''Return all children of node in graph'''
    children = []
    for l in links:
        if l[0] == node:
            children.append(l[1])
        else:
            if l[1] == node:
                children.append(l[0])
    return children

def getBitsNum(numPaths, numStreams):
    '''Return number of bits, that required for genotype of chromosome'''
    powerTwo = 1
    num = 2
    while numPaths > num:
        powerTwo += 1
        num *= 2
    return powerTwo * numStreams

def bonusCoeffFun(load):
    '''Function of bonus coefficient, that needed for correct work of GA'''
    if load <= 0.25:
        return 40
    else:
        if load <= 0.75:
            return 15
        else:
            return 5

def decodeGenotype(person):
    '''Decoding genotype into array of path indexes'''
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

def SDNFitnessFun(person):
    '''Custom controller fitness function'''
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

def inputParameter(msg, errorMsg, lowestValid):
    while True:
        try:
            parameter = int(input(msg))
            if lowestValid != None:
                if parameter < lowestValid:
                    print(errorMsg)
                    continue
        except ValueError:
            print(errorMsg)
            continue
        else:
            break


    return parameter


#
# __main__
#
random.seed()

# Input parameters of SDN
print("Welcome to SDN Genetic Algorithm benchmark!")
nodesNumber = inputParameter("Enter number of nodes in SDN(>=3): ", "Please, enter valid number of nodes", 3)
linksNumber = inputParameter("Enter number of links in SDN(must be not less than the number of nodes): ", "Please, enter valid number of links", nodesNumber) # ! linksNumber >= nodesNumber
minLinkCapacity = inputParameter("Enter minimum link capacity(must be not less than 10): ", "Please, enter valid number of minimum link capacity", 10)
maxLinkCapacity = inputParameter("Enter maximum link capacity(>(minLinkCap + 20)): ", "Please, enter valid number of maximum link capacity", minLinkCapacity + 20)
streamsNumber = inputParameter("Enter number of streams in SDN(>=2): ", "Please, enter valid number of streams", 2) #TODO: Fix issue with one stream in the network

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
            # At first we connected all nodes together, further we use random generation
            if i < nodesNumber:
                nodeFirst = nodes[i]
            else:
                nodeFirst = random.randint(0, nodesNumber - 1)
            if i < nodesNumber - 1:
                nodeSecond = nodes[i + 1]
            else:
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

    print("Generated data:")
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
