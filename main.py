import genetic
import math

# Test fitness function
def fitnessFun(x):
    return 1/((x / 100 - 15) ** 6 + 0.2) - math.sin(x / 100) + 1

answer = genetic.executeGeneticAlgoritm(fitnessFun)

print('\n------------------------')
print('| The Answer is: {0:.4} |'.format(answer))
print('------------------------')