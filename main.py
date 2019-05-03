import sys
import genetic
import random
import datetime
from datetime import timedelta

def findAllPathsUtil(nodes, links, visited, node, goal, path, paths):
    '''Recursive function for finding all paths for stream'''
    visited[node] = True
    path.append(node)

    # !!! UNCOMENT FOR FULL-CONNECTED NETWORK !!!
    #if len(path) <= 3: # Condition for restriction path length (3 nodes: src -> med -> trg)
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
        elif l[1] == node:
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

def penaltyFun(load):
    '''Function of bonus coefficient, that needed for correct work of GA'''
    if load <= 0.05:
        return 1
    else:
        if load <= 0.25:
            return 5
        else:
            if load <= 0.5:
                return 10
            else:
                if load <= 0.75:
                    return 50
                else:
                    if load < 1:
                        return 150
                    else:
                        if load < 2:
                            return 500
                        else:
                            if load < 3:
                                return 1000
                            else:
                                return 10000

def decodeGenotype(person):
    '''Decoding genotype into array of path indexes'''
    global numberStreams
    global streamsPaths
    global numberBitsInGenotype
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
        phenotype.append(int(extractNumber))
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

def isFlowOnLink(flow, link, nidx):
    return flow[nidx] == link[0] and flow[nidx + 1] == link[1] or \
           flow[nidx] == link[1] and flow[nidx + 1] == link[0]

def getNetworkLoad(phenotype):
    global links
    global linksCapacities
    global streams
    global streamsPaths

    # Select paths corresponding to phenotype
    paths = []
    try:
        for i in range(0, len(phenotype)):
            if phenotype[i] >= 0:
                paths.append(streamsPaths[i][phenotype[i]])
    except Exception:
        t, v, tb = sys.exc_info()
        print("i: {}, phenotype[i]: {}".format(i, phenotype[i]))
        raise t, v, tb

    linksTraffic = 0
    for i in range(0, len(links)):
        for j in range(0, len(paths)):
            for k in range(0, len(paths[j]) - 1):
                if isFlowOnLink(paths[j], links[i], k):
                    linksTraffic += streams[j][2]

    linksCapacity = 0
    for i in range(0, len(links)):
        linksCapacity += linksCapacities[i]

    return float(linksTraffic) / float(linksCapacity)


def SDNFitnessFun(person):
    '''Custom controller fitness function'''

    try:
        # Decode genotype
        phenotype = decodeGenotype(person)

        # Calculate network load
        networkLoad = getNetworkLoad(phenotype)

        return float(penaltyFun(networkLoad))
    except Exception:
        t, v, tb = sys.exc_info()
        print(phenotype)
        raise t, v, tb

def inputParameter(msg, errorMsg, lowestValid):
    '''Helps input SDN parameters'''
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

def getRandomSpanningTree(nodes, links):
    '''Gets random spanning tree for first network links generation'''

    # Select root of tree randomly
    checked = [random.randint(0, len(nodes)-1)]
    tree = []
    while len(checked) < len(nodes):

        # Select first node in link only from cheked list
        #   for sake of getting one tree instead of forest
        i = random.randint(0, len(checked)-1)
        # Next node can be whatever random wants but not a loop
        j = random.randint(0, len(nodes)-1)
        while checked[i] == nodes[j] or nodes[j] in checked:
            j = random.randint(0, len(nodes)-1)

        # Add link to tree if it not existed yet
        if not (checked[i], nodes[j]) in tree and not (nodes[j], checked[i]) in tree:
            tree.append((checked[i], nodes[j]))
            checked.append(nodes[j])

    return tree


#
# __main__
#
if __name__ == "__main__":
    random.seed()

    # Input parameters of SDN
    print("Welcome to SDN Genetic Algorithm benchmark!")
    nodesNumber = inputParameter("Enter number of nodes in SDN(>=3): ", "Please, enter valid number of nodes", 3)
    linksNumber = 0 # We assign value after generation full topology (linksNumber >= nodesNumber)
    streamsNumber = inputParameter("Enter number of streams in SDN(>=2): ", "Please, enter valid number of streams", 2) #TODO: Fix issue with one stream in the network
    minLinkCapacity = 10#inputParameter("Enter minimum link capacity(must be not less than 10): ", "Please, enter valid number of minimum link capacity", 10)
    maxLinkCapacity = 100#inputParameter("Enter maximum link capacity(>(minLinkCap + 20)): ", "Please, enter valid number of maximum link capacity", minLinkCapacity + 20)

    # Generate nodes
    nodes = []
    for i in range(0, nodesNumber):
        nodes.append(i)

    # Generate full-connected network links
    linksFull = []
    for i in range(0, nodesNumber):
        for j in range(0, nodesNumber):
            if i != j and not ((i, j) in linksFull or (j, i) in linksFull):
                linksFull.append(tuple([i, j]))

    sumTotalExecutionTimes = 0
    sumGAExecutionTimes = 0
    sumPrepareExecutionTimes = 0
    firstBest = 0
    inadequateCount = 0
    diffMean = 0
    redoCountMean = 0
    print("--------------------------------------------------------------------")
    #
    # Algorithm test loop
    #
    for iteration in range(0, 100):
        print("ITERATION #{0}".format(iteration))

        # Generate links at first as tree
        links = getRandomSpanningTree(nodes, linksFull)

        # And then generate additional bounds
        linksNodesRatio = 1.3
        nodeNum = len(nodes)
        while len(links) < nodeNum * linksNodesRatio: 
            i = random.randint(0, nodeNum-1)
            j = random.randint(0, nodeNum-1)
            while i == j:
                j = random.randint(0, nodeNum-1)

            if not (i, j) in links and not (j, i) in links:
                links.append((i, j))

        # And at now we can gen number of links
        linksNumber = len(links)

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

        print("\nGenerated data:")
        print("Nodes: {0}".format(nodes))
        print("Links: {0}".format(links))
        print("Links capacities: {0}".format(linksCapacities))
        print("Streams (src, trg, reqCapacity): {0}".format(streams))

        # Fix time of preparing algorithms start
        prepareStartTime = datetime.datetime.now()

        # Find paths for current streams
        streamsPaths = []
        for s in streams:
            baz = findAllPaths(nodes, links, s[0], s[1])[:]
            streamsPaths.append(baz)

        print("STREAM PATHS: {}".format(streamsPaths))

        # Calculate array of path variants numbers for util purposes
        numbersPaths = [];
        for s in streamsPaths:
            numbersPaths.append(len(s))

        # Calculate number bits in genotype
        numberStreams = len(streams)
        numberBitsInGenotype = getBitsNum(max(numbersPaths), numberStreams)
        print("NUMBER BITS IN GENOTYPE: {}".format(numberBitsInGenotype))

        # Fix time of preparing algorithms stop and fix time of the GA start
        prepareStopTime = datetime.datetime.now()
        GAStartTime = datetime.datetime.now()

        redoCount = 0
        while True:
            # Execution of the genetic algorithm and receive answer from it
            answer = genetic.executeGeneticAlgoritm(SDNFitnessFun, numberBitsInGenotype, 100, 0.003, True, firstBest)
            phenotype = decodeGenotype(answer)

            # Calculate network loads before and after optimisation
            randomSolutionLoad = getNetworkLoad(decodeGenotype(firstBest)) * 100
            bestSolutionLoad = getNetworkLoad(decodeGenotype(answer)) * 100

            # If result is adequate - proceed, else redo genetic algorithm
            if randomSolutionLoad >= bestSolutionLoad or redoCount > 10:
                break

            redoCount += 1
        
        print("CHROMOSOME: {:b}".format(answer))

        redoCountMean += redoCount

        # Fix time of the GA stop and calculate execution times
        GAStopTime = datetime.datetime.now()
        executionPrepareTime = (prepareStopTime - prepareStartTime).total_seconds()
        executionGATime = (GAStopTime - GAStartTime).total_seconds()
        totalExecutionTime = (GAStopTime - prepareStartTime).total_seconds()

        sumPrepareExecutionTimes += executionPrepareTime
        sumGAExecutionTimes += executionGATime
        sumTotalExecutionTimes += totalExecutionTime

        paths = []
        for i in range(0, len(phenotype)):
            paths.append(streamsPaths[i][phenotype[i]])

        randomPaths = []
        randomPhenotype = decodeGenotype(firstBest)
        for i in range(0, len(randomPhenotype)):
            randomPaths.append(streamsPaths[i][randomPhenotype[i]])

        if randomSolutionLoad < bestSolutionLoad:
            inadequateCount += 1
            print("\n!!!INADEQUATE RESULT DETECTED!!!")
        else:
            difference = randomSolutionLoad - bestSolutionLoad
            print("\nGenetic and random result difference: {0:.3}%".format(difference))
            diffMean += difference
        print("Redo count: {0}\n".format(redoCount))

        print("\nRandom selection of paths: {0}".format(randomPaths))
        print("Best selection of paths: {0}".format(paths))
        print("Random network load (%): {0:.6}".format(randomSolutionLoad))
        print("Best network load (%): {0:.6}".format(bestSolutionLoad))
        print("\nExecution time of prepare algorithms equal {0:.6} milliseconds".format(executionPrepareTime * 1000))
        print("Execution time of the genetic algorithm equal {0:.6} milliseconds".format(executionGATime * 1000))
        print("Total execution time equal {0:.6} milliseconds".format(totalExecutionTime * 1000))
        print("--------------------------------------------------------------------")

    diffMean /= 100
    redoCountMean /= 100
    print("\nSUMMARY:")
    print("Average execution time of prepare algorithms equal {0:.6} milliseconds".format(sumPrepareExecutionTimes * 1000 / 100))
    print("Average execution time of the genetic algorithm equal {0:.6} milliseconds".format(sumGAExecutionTimes * 1000 / 100))
    print("Average total execution time equal {0:.6} milliseconds".format(sumTotalExecutionTimes * 1000 / 100))
    print("Number of inadequate results: {0}".format(inadequateCount))
    print("Genetic and random mean result difference: {0:.3}%".format(diffMean))
    print("Mean redo of inadequate result: {0}".format(redoCountMean))
