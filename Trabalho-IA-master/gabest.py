# Stephen Marsland, 2008, 2014
# Adaptação e correção de bugs por Hendrik Macedo, 2017

# @Anya Best results. Much simplier
import numpy as np
import random
import pylab as pl
import time
import rungame as rg
import choi_yena.utils_.gautils as gautils

Parameters = [(1,5),
	(1,10),
	(1,1000),
	(1,10),
	(1,50),
	(50, 400),
	(1,10),
	(1,1000),
	(10, 10000),
	(1,10),
	(1,10000),
	(0,9)]


def fit(pop):
	mapped = {}
	fitness = np.zeros(np.shape(pop)[0])


	for i, element in enumerate(pop):
		MaxHalite  = 0
		fr = open("halite.txt", "r")
		gautils.save(element, "choi_yena/utils_/parameters.py")
		rg.rungame()
		MaxHalite = fr.readline()
		fitness[i] = MaxHalite
		fr.close()

	return fitness

class ga:

	def __init__(self,stringLength,Parameters,nEpochs=300,populationSize=500,mutationProb=0.05):
		""" Constructor"""
		flag = 0
		self.stringLength = stringLength
		self.Parameters = Parameters
		# Population size should be even
		if np.mod(populationSize,2)==0:
			self.populationSize = populationSize
		else:
			self.populationSize = populationSize+1

		if mutationProb < 0:
			 self.mutationProb = 1/stringLength
		else:
			 self.mutationProb = mutationProb

		self.nEpochs = nEpochs

		self.fitnessFunction = 'fit'

		#Na Codificação por Permutação, cada cromossoma é uma série de números que representa uma posição em uma seqüência
		#Codificação: Os cromossomas descrevem a ordem em que o caixeiro visitará as cidades.``
		self.population = np.zeros((self.populationSize,self.stringLength), dtype=np.int)
		for i in range(self.populationSize):
			for j, element in enumerate(Parameters):
				self.population[i][j]= random.randint(element[0], element[1])
		#self.distances = distances

	def runGA(self):
		"""The basic loop"""
		best_value = np.zeros(self.nEpochs)
		best_order = np.zeros((self.nEpochs,self.stringLength), dtype=np.int)

		for i in range(self.nEpochs):
			# Compute fitness of the population
			fitness = eval(self.fitnessFunction)(self.population)

			# Pick parents -- can do in order since they are randomised
			newPopulation = self.fps(self.population,fitness)

			# Apply the genetic operators
			newPopulation = self.spCrossover(newPopulation)
			newPopulation = self.mutate(newPopulation)


			best_value[i] = max(fitness)
			best_order[i] = self.population[np.argmax(fitness)]
			#print (i, " Ordem: ", best_order[i]," Distancia:",best_value[i])
			self.population = newPopulation

		b_v = max(best_value)
		b_o = best_order[np.argmax(best_value)]

		gautils.log(best_value, best_order, b_v, b_o)
		#return best_order[self.nEpochs-1], best_value[self.nEpochs-1], best_value
		return b_o, b_v, best_value
		#pl.show()


	def fps(self,population,fitness):

		# Scale fitness by total fitness
		fitness = fitness/np.sum(fitness)
		fitness = 10*fitness/fitness.max()

		# Put repeated copies of each string in according to fitness
		# Deal with strings with very low fitness
		j=0
		while np.round(fitness[j])<1:
			j = j+1

		newPopulation = np.kron(np.ones((int(np.round(fitness[j])),1)),population[j,:])

		# Add multiple copies of strings into the newPopulation
		for i in range(j+1,self.populationSize):
			if np.round(fitness[i])>=1:
				newPopulation = np.concatenate((newPopulation,np.kron(np.ones((int(np.round(fitness[i])),1)),population[i,:])),axis=0)

		# Shuffle the order (note that there are still too many)
		indices = list(range(np.shape(newPopulation)[0]))
		np.random.shuffle(indices)
		newPopulation = newPopulation[indices[:self.populationSize],:]
		return newPopulation

	def spCrossover(self,population):
		# Single point crossover
		newPopulation = np.zeros(np.shape(population))
		crossoverPoint = np.random.randint(0,self.stringLength,self.populationSize)
		for i in range(0,self.populationSize,2):
			newPopulation[i,:crossoverPoint[i]] = population[i,:crossoverPoint[i]]
			newPopulation[i+1,:crossoverPoint[i]] = population[i+1,:crossoverPoint[i]]
			newPopulation[i,crossoverPoint[i]:] = population[i+1,crossoverPoint[i]:]
			newPopulation[i+1,crossoverPoint[i]:] = population[i,crossoverPoint[i]:]
		return newPopulation


	def mutate(self,population):
		# Mutation
		whereMutate = np.random.sample(np.shape(population)[0])
		population[np.where(whereMutate < self.mutationProb)] = self.mutateIndividual(population[np.where(whereMutate < self.mutationProb)])
		return population

	def mutateIndividual(self,population):
		# Mutation
		for i in range(np.shape(population)[0]):
			i0 = np.random.randint(self.stringLength)
			i1 = np.random.randint(self.stringLength)
			v = population[i][i0]
			population[i][i0] = population[i][i1]
			population[i][i1] = v
		return population

def runAll():
	import time

	nParameters = 12


#elitismo, torneio, e crossover uniforme não foram implementados a tempo
#falando em tempo, alterei a implementação da execução do GA, para computar o tempo de execução no final da execução,
#e antes de desenhar o gráfico, ao invés de calcular após instanciar o GA.
	print ("\nAlgoritmo Genético")
	pl.ion()
	pl.show()

	plotfig = pl.figure()

	start = time.time()
	iga = ga(nParameters, Parameters, nEpochs=5*nParameters,populationSize=5*nParameters,mutationProb=0)
	result = iga.runGA()
	finish = time.time()
	print ("Ordem:",result[0]," MaxHalite:",result[1])
	print ("Tempo: ",finish-start)
	pl.plot(result[2],'kx-')
	pl.pause(0)

runAll()