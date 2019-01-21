# Stephen Marsland, 2008, 2014
# Adaptação e correção de bugs por Hendrik Macedo, 2017

# @Anya Worst Results. More complete
import numpy as np
import random
import pylab as pl
import time
import rungame as rg

Parameters = [(0,5),
	(0,10),
	(0,1000),
	(0,500),
	(0,9)]






def save(element):
	f = open("parameters.py", "w+")
	f.write(f"viewDistance = {element[0]}\n")
	f.write(f"reward_multiplier = {element[1]}\n")
	f.write(f"maxHaliteToMove = {element[2]}\n")
	f.write(f"maxHaliteToReturn = {element[3]}\n")
	f.write(f"gamma = {element[4]/10}\n")
	return None


def fit(pop):
	mapped = {}
	fitness = np.zeros(np.shape(pop)[0])


	for i, element in enumerate(pop):
	#	aux_element = tuple(int(x) for x in element)
		save(element)
	#	if aux_element not in mapped:

		fitness[i] = rg.rungame()
	#		mapped[aux_element] = fitness[i]
	#	else:
	#		fitness[i] = mapped[aux_element]
	return fitness

class ga:

	def __init__(self,stringLength,Parameters,nEpochs=300,populationSize=500,mutationProb=0.05,crossover='un',nElite=4,tournament=True):
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

		self.crossover = crossover
		self.nElite = nElite
		self.tournment = tournament

		#Na Codificação por Permutação, cada cromossoma é uma série de números que representa uma posição em uma seqüência
		#Codificação: Os cromossomas descrevem a ordem em que o caixeiro visitará as cidades.``
		self.population = np.zeros((self.populationSize,self.stringLength), dtype=np.int)
		for i in range(self.populationSize):
			for j, element in enumerate(Parameters):
				self.population[i][j]= random.randint(element[0], element[1])
		#self.distances = distances

	def runGA(self,plotfig):
		"""The basic loop"""
		pl.ion()
		#plotfig = pl.figure()
		bestfit = np.zeros(self.nEpochs)
		best_order = np.zeros((self.nEpochs,self.stringLength), dtype=np.int)


		for i in range(self.nEpochs):
			# Compute fitness of the population
			fitness = eval(self.fitnessFunction)(self.population)

			# Pick parents -- can do in order since they are randomised
			newPopulation = self.fps(self.population,fitness)

			# Apply the genetic operators
			if self.crossover == 'sp':
				newPopulation = self.spCrossover(newPopulation)
			elif self.crossover == 'un':
				newPopulation = self.uniformCrossover(newPopulation)
			newPopulation = self.mutate(newPopulation)

			# Apply elitism and tournaments if using
			if self.nElite>0:
				newPopulation = self.elitism(self.population,newPopulation,fitness)

			if self.tournament:
				newPopulation = self.tournament(self.population,newPopulation,fitness,self.fitnessFunction)

			bestfit[i] = max(fitness)
			best_order[i] = self.population[np.argmax(fitness)]
			self.population = newPopulation

			#if (np.mod(i,1)==0):
			#pl.plot([i],[fitness.max()],'r+')
		b_v = max(bestfit)
		b_o = best_order[np.argmax(bestfit)]
		return b_o, b_v, bestfit
		#pl.plot(bestfit,'kx-')
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

	def uniformCrossover(self,population):
		# Uniform crossover
		newPopulation = np.zeros(np.shape(population))
		which = np.random.rand(self.populationSize,self.stringLength)
		which1 = which>=0.5
		for i in range(0,self.populationSize,2):
			newPopulation[i,:] = population[i,:]*which1[i,:] + population[i+1,:]*(1-which1[i,:])
			newPopulation[i+1,:] = population[i,:]*(1-which1[i,:]) + population[i+1,:]*which1[i,:]
		return newPopulation

	def mutate(self,population):
		# Mutation
		whereMutate = np.random.rand(np.shape(population)[0],np.shape(population)[1])
		population[np.where(whereMutate < self.mutationProb)] = 1 - population[np.where(whereMutate < self.mutationProb)]
		return population

	def elitism(self,oldPopulation,population,fitness):
		best = np.argsort(fitness)
		best = np.squeeze(oldPopulation[best[-self.nElite:],:])
		indices = list(range(np.shape(population)[0]))
		np.random.shuffle(indices)
		population = population[indices,:]
		population[0:self.nElite,:] = best
		return population

	def tournament(self,oldPopulation,population,fitness,fitnessFunction):
		newFitness = eval(self.fitnessFunction)(population)
		for i in range(0,np.shape(population)[0],2):
			f = np.concatenate((fitness[i:i+2],newFitness[i:i+2]),axis=0)
			indices = np.argsort(f)
			if indices[-1]<2 and indices[-2]<2:
				population[i,:] = oldPopulation[i,:]
				population[i+1,:] = oldPopulation[i+1,:]
			elif indices[-1]<2:
				if indices[0]>=2:
					population[i+indices[0]-2,:] = oldPopulation[i+indices[-1]]
				else:
					population[i+indices[1]-2,:] = oldPopulation[i+indices[-1]]
			elif indices[-2]<2:
				if indices[0]>=2:
					population[i+indices[0]-2,:] = oldPopulation[i+indices[-2]]
				else:
					population[i+indices[1]-2,:] = oldPopulation[i+indices[-2]]
		return population
def runAll():
	import time

	nParameters = 5


#elitismo, torneio, e crossover uniforme não foram implementados a tempo
#falando em tempo, alterei a implementação da execução do GA, para computar o tempo de execução no final da execução,
#e antes de desenhar o gráfico, ao invés de calcular após instanciar o GA.
	print ("\nAlgoritmo Genético")
	pl.ion()
	pl.show()

	plotfig = pl.figure()
	start = time.time()
	iga = ga(nParameters, Parameters, nEpochs=100*nParameters,populationSize=100*nParameters,mutationProb=0)
	finish = time.time()
	result = iga.runGA(plotfig)
	print ("Ordem:",result[0]," Distancia:",result[1])
	print ("Tempo de execução: ",finish-start)
	pl.plot(result[2],'kx-')
	pl.pause(0)

runAll()