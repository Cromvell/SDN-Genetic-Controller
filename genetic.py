import random

def select(chromosomes, fitness):
    '''Doing selection'''
    fitSum = 0
    lenfit = len(fitness)
    for i in range(0, lenfit):
        fitSum += fitness[i]

    sectors = []
    for i in range(0, lenfit):
        sectors.append(fitness[i] * 100 / fitSum)

    parents = []
    for i in range(0, lenfit):
        rnd = random.randrange(0, 100, 1)
        angle = 0
        j = 0
        while True:
            angle += sectors[j]
            if angle > rnd: break
            j += 1
        parents.append(chromosomes[j])

    return parents

def cross(parents, lenOfChromosome):
    '''Crossing parents pool'''
    pairs = []
    lenParents = len(parents)

    for i in range(0, lenParents // 2):
        p1 = random.randrange(0, lenParents - 2 * i, 1)
        while True:
            p2 = random.randrange(0, lenParents - 2 * i, 1)
            if p2 != p1: break # For exclude collisions p1 with p2
        pairs.append([parents[p1], parents[p2]])

        del parents[p1]
        if p2 < p1:
            del parents[p2] 
        else:
            del parents[p2 - 1] # After deleting parents[p2] index p1 might be shifted

    pointsOfCross = []
    for i in range(0, lenParents // 2):
        pointsOfCross.append(random.randrange(1, lenOfChromosome // 2 + 1, 1))

    children = []
    p1Part = p2Part = 0
    for i in range(0, lenParents // 2):
        for j in range(0, pointsOfCross[i] + 1):
            # Save bits, which belong to interval from end of genome to point of cross
            p1Part = p1Part | (pairs[i][0] & (1 << j))
            p2Part = p2Part | (pairs[i][1] & (1 << j))

            # Set to zero saved bits
            pairs[i][0] = pairs[i][0] & ~(1 << j)
            pairs[i][1] = pairs[i][1] & ~(1 << j)

        children.append(pairs[i][0] | p2Part)
        children.append(pairs[i][1] | p1Part)

        p1Part = p2Part = 0

    return children

def mutation(population, lengthOfChromosome, chanceOfMutation, outputEnable = False, outputFile = None):
    '''Doing mutation'''
    for i in range(0, len(population)):
        if random.uniform(0, 100) < chanceOfMutation * 100:
            before = population[i]
            mutatNumber = 1 << random.randrange(0, lengthOfChromosome + 1, 1)
            population[i] = population[i] ^ mutatNumber
            if outputEnable: outputFile.write('!!! MUTATION !!! Before: {0:b}({0}) After: {1:b}({1})\n'.format(before, population[i]))

def chooseTheBest(fitness):
    '''Choose the best person from population'''
    maximum = fitness[0]
    for i in range(1, len(fitness)):
        if fitness[i] > maximum:
            maximum = fitness[i]

    return maximum

def outputInfo(info, lengthOfChromosome, sizeOfPopulation, generationNumber, outputFile, closeFile = False):
    '''Show information about generation'''

    outputFile.write('\nGeneration #{0}:\n'.format(generationNumber))
    outputFile.write('{0} | {1} |    {2}    |   {3}\n'.format('Current population', 'Fitness', 'Parents pool', 'New population'))

    for i in range(0, sizeOfPopulation):
        if i < (sizeOfPopulation - 1) or sizeOfPopulation % 2 == 0:
            outputFile.write('{0:20} {1:9} {2:20} {3}\n'.format('{0:0{1}b}({0})'.format(info[0][i], lengthOfChromosome), \
                                                         '{0:.4}'.format(info[1][i]), \
                                                         '{0:0{1}b}({0})'.format(info[2][i], lengthOfChromosome), \
                                                         '{0:0{1}b}({0})'.format(info[3][i], lengthOfChromosome), \
                                                         lengthOfChromosome))
    if closeFile: outputFile.close()

def executeGeneticAlgoritm(fitnessFunction, lengthOfChromosome = 12, sizeOfPopulation = 100, generateInfoFile = False):
    '''Execute genetic algorithm'''
    if generateInfoFile:
        genInfo = []
        outFile = open('output.log', 'w')
    genNumber = 1
    random.seed()

    # Population initialisation
    population = []
    for i in range(0, sizeOfPopulation):
        population.append(random.getrandbits(lengthOfChromosome))

    # TODO: Do algorithm without break
    while True:
        if generateInfoFile: genInfo.append(population[:])

        # Fitness calculation
        fitness = []
        for i in population:
            fitness.append(fitnessFunction(i / 100.0))
        if generateInfoFile: genInfo.append(fitness[:])

        # Stop condition
        if genNumber >= 100: break

        # Selection
        parents = select(population, fitness)
        if generateInfoFile: genInfo.append(parents[:])

        # Crossing
        population = cross(parents, lengthOfChromosome)
        if generateInfoFile: genInfo.append(population[:])


        # Mutation
        if generateInfoFile:
            mutation(population, lengthOfChromosome, 0.01, True, outFile)
        else:
            mutation(population, lengthOfChromosome, 0.01)

        if generateInfoFile: outputInfo(genInfo, lengthOfChromosome, sizeOfPopulation, genNumber, outFile, True if genNumber >= 99 else False)

        # Clear information list
        if generateInfoFile: del genInfo[:]

        genNumber += 1

    return chooseTheBest(fitness)